import logging
import shutil
import time
import rasterio
import numpy as np
from rasterio.windows import from_bounds

logging.basicConfig(level=logging.INFO)

t0 = time.time()

# adbpo_path = "/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_l_merged_3035_2m.tif"
# milano_path = "/home/admin_climatecharted_com/data/Altezza/Milano_TR500_2m.tif"
# out_path = "/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_l_merged_milano_tr500_3035_2m.tif"

adbpo_path = "/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_l_merged_3035_5m.tif"
milano_path = "/home/admin_climatecharted_com/data/Altezza/Milano_TR500_5m.tif"
out_path = "/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_l_merged_milano_tr500_3035_5m.tif"

# -------------------------
# STEP 1: COPY BASE RASTER
# -------------------------
logging.info("Copying base raster (fast, no pixel processing)")
shutil.copy(adbpo_path, out_path)

with rasterio.open(out_path, "r+") as dst, rasterio.open(milano_path) as mil_src:

    logging.info("Opened output raster in update mode")

    # -------------------------
    # READ MILANO
    # -------------------------
    mil_data = mil_src.read(1)
    mil_nodata = mil_src.nodata

    # -------------------------
    # COMPUTE WINDOW
    # -------------------------
    window = from_bounds(*mil_src.bounds, transform=dst.transform)
    window = window.round_offsets().round_lengths()

    logging.info(f"Window: {window}")

    # -------------------------
    # READ ONLY NEEDED ADBPO PIXELS
    # -------------------------
    adb_data = dst.read(1, window=window)
    adb_nodata = dst.nodata

    # -------------------------
    # MERGE LOGIC
    # -------------------------
    adb_valid = adb_data != adb_nodata
    mil_valid = mil_data != mil_nodata

    out_data = adb_data.copy()

    both_valid = adb_valid & mil_valid
    only_mil = (~adb_valid) & mil_valid

    out_data[both_valid] = np.maximum(adb_data[both_valid], mil_data[both_valid])
    out_data[only_mil] = mil_data[only_mil]

    logging.info("Writing only Milano window")

    # -------------------------
    # WRITE ONLY WINDOW
    # -------------------------
    dst.write(out_data, 1, window=window)

logging.info(f"Done in {time.time()-t0:.2f}s")