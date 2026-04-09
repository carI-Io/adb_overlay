import os
import subprocess
import logging
from sqlalchemy import create_engine, text

export PGHOST=91.98.183.177
export PGDB=climatecharted_geo
export PGUSER=postgres
export PGPASSWORD=pza!gud2ZMN_fxq9ycr
export PGPORT=6432

# psql -d "$PGDB" -U "$PGUSER" -h "$PGHOST" -p "$PGPORT"

def upload_file_to_postgis(
    raster_file: str,
    table_name: str,
    db_envs: list[str],
    epsg: int,
    tile_size: str = "128x128"
    ):
    """
    Upload a raster file to multiple PostGIS databases.

    Parameters
    ----------
    raster_file : str
        Path to the raster file (.tif) to upload.
    table_name : str
        Target table name (e.g., 'windstorm_footlogging.info').
    db_envs : list[str]
        List of suffixes for environment variables (e.g., ['DEV', 'PROD']).
    epsg : int, optional
        Spatial reference ID (default: 4326).
    tile_size : str, optional
        Raster tiling size for raster2pgsql (default: '1000x1000').
    """
    
    if not os.path.isfile(raster_file):
        raise FileNotFoundError(f"Raster file not found: {raster_file}")
    
    for env in db_envs:
        DBHOST = os.getenv(f"PGHOST_{env}") or os.getenv("PGHOST")
        DBNAME = os.getenv(f"PGDB_{env}") or os.getenv("PGDB")
        DBUSER = os.getenv(f"PGUSER_{env}") or os.getenv("PGUSER")
        DBPASSWORD = os.getenv(f"PGPASSWORD_{env}") or os.getenv("PGPASSWORD")
        DBPORT = os.getenv(f"PGPORT_{env}") or os.getenv("PGPORT")

        logging.info(f"\n--- Connecting to {env} database: {DBNAME} ---")
        engine = create_engine(f"postgresql://{DBUSER}:{DBPASSWORD}@{DBHOST}:{DBPORT}/{DBNAME}")

        with engine.connect() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))

            postgis_version = connection.execute(text("SELECT postgis_version();")).fetchone()
            logging.info(f"PostGIS version: {postgis_version[0]}")

            geom_type = connection.execute(text("SELECT * FROM pg_type WHERE typname = 'geometry';")).fetchone()
            logging.info("Geometry type exists." if geom_type else "Geometry type does NOT exist.")

        logging.info("Database connection verified.")

        command = (
            f'raster2pgsql -s {epsg} -I -C -M "{raster_file}" '
            f'-t {tile_size} public.{table_name} | '
            f'psql -d {DBNAME} -U {DBUSER} -h {DBHOST} -p {DBPORT}'
        )

        env_vars = os.environ.copy()
        env_vars["PGPASSWORD"] = DBPASSWORD

        logging.info(f"Uploading raster '{table_name}' to {env} DB...")
        result = subprocess.run(command, shell=True, env=env_vars, capture_output=True, text=True)

        if result.returncode == 0:
            logging.info(f"Successfully uploaded '{table_name}' to {DBNAME}.")
        else:
            logging.info(f"Error uploading to {DBNAME}: {result.stderr}")

        logging.info("-" * 80)

TABLE_NAME = "adbpo_pgra2027_l_merged_milano_tr500_3035_5m"
RASTER_FILE = "/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_l_merged_milano_tr500_3035_5m.tif"

upload_file_to_postgis(
    raster_file=RASTER_FILE,
    table_name=TABLE_NAME,
    epsg=3035,
    tile_size='128x128',
    db_envs=["WEBGIS"],  
)