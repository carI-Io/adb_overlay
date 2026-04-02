import logging
import time
import rasterio
import numpy as np
from rasterio.windows import from_bounds

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("=== START MERGE PROCESS ===")
t0 = time.time()

adbpo_path = "/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_l_merged_3035_2m.tif"
milano_path = "/home/admin_climatecharted_com/data/Altezza/Milano_TR500_2m.tif"
out_path = "/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_l_merged_milano_tr500_3035_2m.tif"

with rasterio.open(adbpo_path) as adb_src, rasterio.open(milano_path) as mil_src:

    logging.info("Opened input rasters")

    # -------------------------
    # READ MILANO
    # -------------------------
    t = time.time()
    mil_data = mil_src.read(1)
    mil_nodata = mil_src.nodata
    logging.info(f"Milano raster loaded: shape={mil_data.shape}, nodata={mil_nodata}, time={time.time()-t:.2f}s")

    # -------------------------
    # COMPUTE WINDOW
    # -------------------------
    t = time.time()
    window = from_bounds(*mil_src.bounds, transform=adb_src.transform)
    window = window.round_offsets().round_lengths()

    logging.info(
        f"Computed window in adbpo grid: "
        f"row_off={window.row_off}, col_off={window.col_off}, "
        f"height={window.height}, width={window.width}, "
        f"time={time.time()-t:.2f}s"
    )

    # -------------------------
    # READ ADBPO WINDOW
    # -------------------------
    t = time.time()
    adb_data = adb_src.read(1, window=window)
    adb_nodata = adb_src.nodata
    logging.info(f"ADBPO window loaded: shape={adb_data.shape}, nodata={adb_nodata}, time={time.time()-t:.2f}s")

    # -------------------------
    # MASKS + MERGE LOGIC
    # -------------------------
    t = time.time()
    adb_valid = adb_data != adb_nodata
    mil_valid = mil_data != mil_nodata

    out_data = adb_data.copy()

    both_valid = adb_valid & mil_valid
    only_mil = (~adb_valid) & mil_valid

    logging.info(
        f"Pixel stats → both_valid: {both_valid.sum()}, "
        f"only_mil: {only_mil.sum()}, "
        f"total: {out_data.size}"
    )

    out_data[both_valid] = np.maximum(adb_data[both_valid], mil_data[both_valid])
    out_data[only_mil] = mil_data[only_mil]

    logging.info(f"Merge logic applied in {time.time()-t:.2f}s")

    # -------------------------
    # WRITE OUTPUT
    # -------------------------
    profile = adb_src.profile.copy()

    profile.update(
        BIGTIFF="YES",
        tiled=True,
        compress="deflate",
        predictor=2
    )
    logging.info("Starting output write (this is the slow part)")

    t_write = time.time()

    with rasterio.open(out_path, "w", **profile) as dst:

        total_blocks = sum(1 for _ in adb_src.block_windows(1))
        logging.info(f"Total blocks to write: {total_blocks}")

        t_blocks = time.time()
        for i, (ji, w) in enumerate(adb_src.block_windows(1), start=1):

            dst.write(adb_src.read(1, window=w), 1, window=w)

            # log every N blocks (avoid spam)
            if i % 500 == 0:
                logging.info(f"Written {i}/{total_blocks} blocks ({(i/total_blocks)*100:.1f}%)")

        logging.info(f"Finished writing base raster in {time.time()-t_blocks:.2f}s")

        # overwrite Milano area
        t_over = time.time()
        dst.write(out_data, 1, window=window)
        logging.info(f"Milano window overwrite completed in {time.time()-t_over:.2f}s")

    logging.info(f"Total write time: {time.time()-t_write:.2f}s")

logging.info(f"=== PROCESS COMPLETED in {time.time()-t0:.2f}s ===")