#!/bin/bash

set -euo pipefail

# ---- INPUT PARAMETERS ----
RASTER_FILE=$1
TABLE_NAME=$2
EPSG=$3
TILE_SIZE=$4

# ---- CONFIG ----
CHUNK_SIZE=2000
MAX_RETRIES=3
TMP_DIR="/tmp/raster_chunks_$$"

# ---- VALIDATION ----
if [ -z "$RASTER_FILE" ] || [ -z "$TABLE_NAME" ] || [ -z "$EPSG" ] || [ -z "$TILE_SIZE" ]; then
  echo "Usage: $0 <RASTER_FILE> <TABLE_NAME> <EPSG> <TILE_SIZE>"
  exit 1
fi

if [ -z "$PGHOST" ] || [ -z "$PGDB" ] || [ -z "$PGUSER" ] || [ -z "$PGPORT" ]; then
  echo "Error: PGHOST, PGDB, PGUSER, PGPORT must be set"
  exit 1
fi

mkdir -p "$TMP_DIR"

echo "Reading raster metadata..."

read WIDTH HEIGHT <<< $(gdalinfo "$RASTER_FILE" | grep "Size is" | sed -E 's/.*Size is ([0-9]+), ([0-9]+)/\1 \2/')

echo "Raster size: ${WIDTH} x ${HEIGHT}"

echo "Loading raster into $PGDB.public.$TABLE_NAME..."

FIRST_CHUNK=true
CHUNK_ID=0

for (( x=0; x<WIDTH; x+=CHUNK_SIZE )); do
  for (( y=0; y<HEIGHT; y+=CHUNK_SIZE )); do

    # ---- HANDLE EDGE WINDOWS ----
    XSIZE=$CHUNK_SIZE
    YSIZE=$CHUNK_SIZE

    if (( x + XSIZE > WIDTH )); then
      XSIZE=$((WIDTH - x))
    fi

    if (( y + YSIZE > HEIGHT )); then
      YSIZE=$((HEIGHT - y))
    fi

    CHUNK_FILE="$TMP_DIR/chunk_${CHUNK_ID}.tif"

    echo "Creating chunk $CHUNK_ID (x=$x, y=$y, size=${XSIZE}x${YSIZE})..."

    gdal_translate \
      -of GTiff \
      -srcwin $x $y $XSIZE $YSIZE \
      "$RASTER_FILE" \
      "$CHUNK_FILE" \
      >/dev/null 2>&1

    if [ ! -s "$CHUNK_FILE" ]; then
      echo "Skipping empty chunk $CHUNK_ID"
      continue
    fi

    echo "Loading chunk $CHUNK_ID..."

    RETRY=0
    SUCCESS=false

    while [ $RETRY -lt $MAX_RETRIES ]; do

      if [ "$FIRST_CHUNK" = true ]; then
        MODE="-c"
        INDEX_FLAG=""   # create index later
      else
        MODE="-a"
        INDEX_FLAG=""
      fi

      if raster2pgsql \
        -s "$EPSG" \
        -C -M -Y \
        -t "$TILE_SIZE" \
        $MODE \
        $INDEX_FLAG \
        "$CHUNK_FILE" public."$TABLE_NAME" \
        | PGPASSWORD="${PGPASSWORD:-}" psql \
            -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDB" \
            -v ON_ERROR_STOP=1 \
            -c "SET statement_timeout = 0;" \
            -f -; then

        SUCCESS=true
        FIRST_CHUNK=false
        break
      else
        echo "Chunk $CHUNK_ID failed (attempt $((RETRY+1)))"
        RETRY=$((RETRY+1))
        sleep 2
      fi
    done

    if [ "$SUCCESS" = false ]; then
      echo "ERROR: Chunk $CHUNK_ID failed after $MAX_RETRIES attempts"
      exit 1
    fi

    rm -f "$CHUNK_FILE"
    CHUNK_ID=$((CHUNK_ID+1))

  done
done

echo "Cleaning up..."
rm -rf "$TMP_DIR"

echo "Creating spatial index..."
PGPASSWORD="${PGPASSWORD:-}" psql \
  -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDB" \
  -c "CREATE INDEX IF NOT EXISTS ${TABLE_NAME}_rast_gist ON public.\"$TABLE_NAME\" USING GIST (ST_ConvexHull(rast));"

echo "Done."