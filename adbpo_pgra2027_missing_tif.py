import logging
from pathlib import Path
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

logging.basicConfig(level=logging.INFO)

logging.info("Start tracking missing tif")
# -----------------------------
# Paths and parameters
# -----------------------------
src_folder = Path(r"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_l")
dst_res = 2  # meters
dst_crs = "EPSG:3035"
dst_folder = Path(f"/home/admin_climatecharted_com/data/adb_po_pgra_2027_l_3035_{dst_res}m")
dst_folder2 = Path(f"/home/admin_climatecharted_com/data/adb_po_pgra_2027_l_3035_{dst_res}m_2")
dst_folder.mkdir(exist_ok=True)
dst_folder2.mkdir(exist_ok=True)

# -----------------------------
# List all TIFFs in source and destination
# -----------------------------

src_files = set(f.name for f in src_folder.glob("*.tif"))
logging.info(f"Found {len(src_files)} TIFF files in {src_folder}: {src_files}")
dst_files = set(f.name for f in dst_folder.glob("*.tif"))
logging.info(f"Found {len(dst_files)} TIFF files in {dst_folder}: {dst_files}")

src_files = list(src_folder.glob("*.tif"))

# # Select only files missing in the destination folder
# to_process = [f for f in src_files if (f.stem + f"_3035_{dst_res}m.tif") not in dst_files]
# logging.info(f"Found {len(to_process)} missing files to reproject.")

# # -----------------------------
# # Reproject missing files
# # -----------------------------
# for idx, f in enumerate(to_process, 1):
#     out_file = dst_folder / (f.stem + f"_3035_{dst_res}m.tif")
#     out_file2 = dst_folder2 / (f.stem + f"_3035_{dst_res}m.tif")
    
#     with rasterio.open(f) as src:
#         transform, width, height = calculate_default_transform(
#             src.crs, dst_crs, src.width, src.height, *src.bounds, resolution=dst_res
#         )
        
#         kwargs = src.meta.copy()
#         kwargs.update({
#             "crs": dst_crs,
#             "transform": transform,
#             "width": width,
#             "height": height,
#             "dtype": "float32",
#             "nodata": -9999.0,
#             "compress": "DEFLATE",
#             "tiled": True,
#             "predictor": 2
#         })
        
#         # with rasterio.open(out_file, "w", **kwargs) as dst:
#         #     for i in range(1, src.count + 1):
#         #         reproject(
#         #             source=rasterio.band(src, i),
#         #             destination=rasterio.band(dst, i),
#         #             src_transform=src.transform,
#         #             src_crs=src.crs,
#         #             dst_transform=transform,
#         #             dst_crs=dst_crs,
#         #             resampling=Resampling.bilinear,
#         #             src_nodata=src.nodata,
#         #             dst_nodata=kwargs["nodata"]
#         #         )
#         # logging.info(f"[{idx}/{len(to_process)}] Reprojected {f.name} -> {out_file.name}")
        
#         with rasterio.open(out_file2, "w", **kwargs) as dst:
#             for i in range(1, src.count + 1):
#                 reproject(
#                     source=rasterio.band(src, i),
#                     destination=rasterio.band(dst, i),
#                     src_transform=src.transform,
#                     src_crs=src.crs,
#                     dst_transform=transform,
#                     dst_crs=dst_crs,
#                     resampling=Resampling.bilinear,
#                     src_nodata=src.nodata,
#                     dst_nodata=kwargs["nodata"]
#                 )
#         logging.info(f"[{idx}/{len(to_process)}] Reprojected {f.name} ->{out_file2.name}")

# logging.info("All missing files reprojected successfully.")