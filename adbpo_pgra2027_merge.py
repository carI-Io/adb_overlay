import logging
logging.basicConfig(level=logging.INFO)
from pathlib import Path
from osgeo import gdal
import rasterio
import numpy as np
from rasterio.warp import calculate_default_transform, reproject, Resampling

logging.info("Start merge")

rasters = [
    r"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_h_3035_2m/merged_3035_2m.tif",
    r"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_m_3035_2m/merged_3035_2m.tif",
    r"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_l_3035_2m/merged_3035_2m.tif"
]

# Open rasters and collect metadata
datasets = [rasterio.open(r) for r in rasters]

# Verify they align (crs, transform, shape)
for ds in datasets:
    logging.info(ds.name)
    logging.info(f"CRS: {ds.crs}")
    logging.info(f"Transform: {ds.transform}")
    logging.info(f"Shape: {ds.height} {ds.width}")
    logging.info("----------")

arrays = [ds.read(1) for ds in datasets]
merged = np.max(np.stack(arrays, axis=0), axis=0)

# Save merged raster
out_meta = datasets[0].meta.copy()
out_meta.update({
    "driver": "GTiff",
    "dtype": merged.dtype,
    "count": 1
})

# output_path = r"D:\data\HZRD_Flood\ADB_PO_PGRA_2027\Altezza\adbpo_pgra2027_max_3035_2m.tif"
output_path = r"/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_max_3035_2m.tif"
with rasterio.open(output_path, "w", **out_meta) as dest:
    dest.write(merged, 1)

logging.info(f"4. Merged raster saved at {output_path}")

# Close datasets
for ds in datasets:
    ds.close()