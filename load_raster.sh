#!/bin/bash

# ---- INPUT PARAMETERS ----
RASTER_FILE=$1
TABLE_NAME=$2
EPSG=$3
TILE_SIZE=$4

# ---- VALIDATION ----
if [ -z "$RASTER_FILE" ] || [ -z "$TABLE_NAME" ] || [ -z "$EPSG" ] || [ -z "$TILE_SIZE" ]; then
  echo "Usage: $0 <RASTER_FILE> <TABLE_NAME> <EPSG> <TILE_SIZE>"
  exit 1
fi

# ---- CHECK REQUIRED ENV VARS ----
if [ -z "$PGHOST" ] || [ -z "$PGDB" ] || [ -z "$PGUSER" ] || [ -z "$PGPORT" ]; then
  echo "Error: PGHOST, PGDB, PGUSER, PGPORT must be set"
  exit 1
fi

# ---- EXECUTION ----
echo "Loading raster into $PGDB.$TABLE_NAME..."

raster2pgsql -s "$EPSG" -I -C -M "$RASTER_FILE" -t "$TILE_SIZE" public."$TABLE_NAME" \
| psql -d "$PGDB" -U "$PGUSER" -h "$PGHOST" -p "$PGPORT"

echo "Done."