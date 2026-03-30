import rasterio
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

rasters = [
    r"/home/admin_climatecharted_com/data/ADB/adbpo_pgra2027adbpo_pgra2027_h_merged_3035_2m.tif",
    r"/home/admin_climatecharted_com/data/ADB/adbpo_pgra2027adbpo_pgra2027_m_merged_3035_2m.tif",
    r"/home/admin_climatecharted_com/data/ADB/adbpo_pgra2027adbpo_pgra2027_l_merged_3035_2m.tif"
]
datasets = [rasterio.open(r) for r in rasters]
logging.info("Raster datasets opened"
             )
arrays = [ds.read(1) for ds in datasets]
merged = np.max(np.stack(arrays, axis=0), axis=0)
logging.info("Rasters merged using maximum value")

out_meta = datasets[0].meta.copy()
out_meta.update({
    "driver": "GTiff",
    "dtype": merged.dtype,
    "count": 1
})

output_path = r"/home/admin_climatecharted_com/data/ADB/adbpo_pgra2027_max_3035_2m.tif"
with rasterio.open(output_path, "w", **out_meta) as dest:
    dest.write(merged, 1)

logging.info(f"Merged raster saved at {output_path}")

# Close datasets
for ds in datasets:
    ds.close()