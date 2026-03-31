import logging
logging.basicConfig(level=logging.INFO)
from pathlib import Path
from osgeo import gdal
import rasterio
import numpy as np

folder = Path(r"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_h_3035_2m")
# folder = Path(r"D:/data/HZRD_Flood/ADB_PO_PGRA_2027/Altezza/adb_po_pgra_2027_h_3035_2m")

tif_files = list(folder.glob("*.tif"))

vrt_path = folder / "merged.vrt"
out_path = folder / "merged_3035_2m.tif"

logging.info("Start")

# Build VRT (virtual mosaic)
gdal.BuildVRT(str(vrt_path), [str(f) for f in tif_files])

# Translate VRT to final compressed GeoTIFF
gdal.Translate(
    str(out_path),
    str(vrt_path),
    creationOptions=[
        "COMPRESS=DEFLATE",
        "BIGTIFF=YES",
        "TILED=YES"
    ]
)
logging.info(f"1. Merged raster saved at: {out_path}")

folder = Path(r"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_m_3035_2m")
# folder = Path(r"D:/data/HZRD_Flood/ADB_PO_PGRA_2027/Altezza/adb_po_pgra_2027_m_3035_2m")
tif_files = list(folder.glob("*.tif"))

vrt_path = folder / "merged.vrt"
out_path = folder / "merged_3035_2m.tif"

# Build VRT (virtual mosaic)
gdal.BuildVRT(str(vrt_path), [str(f) for f in tif_files])

# Translate VRT to final compressed GeoTIFF
gdal.Translate(
    str(out_path),
    str(vrt_path),
    creationOptions=[
        "COMPRESS=DEFLATE",
        "BIGTIFF=YES",
        "TILED=YES"
    ]
)
logging.info(f"2. Merged raster saved at: {out_path}")

folder = Path(r"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_l_3035_2m")
# folder = Path(r"D:/data/HZRD_Flood/ADB_PO_PGRA_2027/Altezza/adb_po_pgra_2027_l_3035_2m")
tif_files = list(folder.glob("*.tif"))

vrt_path = folder / "merged.vrt"
out_path = folder / "merged_3035_2m.tif"

# Build VRT (virtual mosaic)
gdal.BuildVRT(str(vrt_path), [str(f) for f in tif_files])

# Translate VRT to final compressed GeoTIFF
gdal.Translate(
    str(out_path),
    str(vrt_path),
    creationOptions=[
        "COMPRESS=DEFLATE",
        "BIGTIFF=YES",
        "TILED=YES"
    ]
)
logging.info(f"3. Merged raster saved at: {out_path}")

# Paths to your rasters
# rasters = [
#     r"D:\data\HZRD_Flood\ADB_PO_PGRA_2027\Altezza\adb_po_pgra_2027_h_3035_2m\adbpo_pgra2027_h_merged_3035_2m.tif",
#     r"D:\data\HZRD_Flood\ADB_PO_PGRA_2027\Altezza\adb_po_pgra_2027_m_3035_2m\adbpo_pgra2027_m_merged_3035_2m.tif",
#     r"D:\data\HZRD_Flood\ADB_PO_PGRA_2027\Altezza\adb_po_pgra_2027_l_3035_2m\adbpo_pgra2027_l_merged_3035_2m.tif"
# ]
rasters = [
    r"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_h_3035_2m/adbpo_pgra2027_h_merged_3035_2m.tif",
    r"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_m_3035_2m/adbpo_pgra2027_m_merged_3035_2m.tif",
    r"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_l_3035_2m/adbpo_pgra2027_l_merged_3035_2m.tif"
]



# Open rasters and collect metadata
datasets = [rasterio.open(r) for r in rasters]

# Verify they align (crs, transform, shape)
for ds in datasets:
    logging.info(ds.name)
    logging.info("CRS:", ds.crs)
    logging.info("Transform:", ds.transform)
    logging.info("Shape:", ds.height, ds.width)
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