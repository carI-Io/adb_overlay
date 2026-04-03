import logging
logging.basicConfig(level=logging.INFO)
from pathlib import Path
from osgeo import gdal
import rasterio
import numpy as np
from rasterio.warp import calculate_default_transform, reproject, Resampling




# l ==================================================================================================================
logging.info("adb_po_pgra_2027_l: start")
folder = Path(r"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_l")
tif_files = list(folder.glob("*.tif"))
logging.info(f"Found {len(tif_files)} TIFF files in {folder}")

dst_crs = "EPSG:3035"
dst_res = 5  # meters

folder_new = Path(f"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_l_3035_{dst_res}m")
folder_new.mkdir(exist_ok=True)  # create folder if it doesn't exist

for idx, f in enumerate(tif_files):
    out_file = folder_new / (f.stem + f"_3035_{dst_res}m.tif")
    
    with rasterio.open(f) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds, resolution=dst_res
        )
        
        kwargs = src.meta.copy()
        kwargs.update({
            "crs": dst_crs,
            "transform": transform,
            "width": width,
            "height": height,
            "dtype": "float32",
            "nodata": -9999.0,  # <-- safe Float32 nodata,
            "compress": "DEFLATE",  # optional compression
            "tiled": True,           # recommended for large rasters
            "predictor": 2           # improves compression for floats
        })
        
        with rasterio.open(out_file, "w", **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.bilinear,
                    src_nodata=src.nodata,  # ensure nodata is handled
                    dst_nodata=kwargs["nodata"]
                )
    logging.info(f"[{idx+1}/{len(tif_files)}] Reprojected {f.name} -> {out_file.name}")    

tif_files = list(folder_new.glob("*.tif"))
logging.info(f"Found {len(tif_files)} TIFF files in {folder_new}")

vrt_path = Path(r"/home/admin_climatecharted_com/data/Altezza") / "adbpo_pgra2027_l_merged.vrt"
out_4326 = Path(r"/home/admin_climatecharted_com/data/Altezza") / f"adbpo_pgra2027_l_merged_4326_{dst_res}m.tif"

gdal.BuildVRT(str(vrt_path), [str(f) for f in tif_files])
logging.info(f"VRT built at {vrt_path}")

out_3035 = Path(r"/home/admin_climatecharted_com/data/Altezza") / f"adbpo_pgra2027_l_merged_3035_{dst_res}m.tif"
gdal.Translate(
    str(out_3035),
    str(vrt_path),
    creationOptions=[
        "COMPRESS=DEFLATE",
        "BIGTIFF=YES",
        "TILED=YES",
        "PREDICTOR=2"
    ]
)
logging.info(f"3. Merged raster saved in EPSG:3035 at: {out_3035}")


# gdal.Warp(
#     str(out_4326),
#     str(out_3035),
#     format="GTiff",
#     dstSRS="EPSG:4326",  
#     creationOptions=[
#         "COMPRESS=DEFLATE",
#         "BIGTIFF=YES",
#         "TILED=YES",
#         "PREDICTOR=2"        
#     ]
# )
# logging.info(f"3. Merged raster saved in EPSG:4326 at: {out_4326}")




# # h =============================================================================================
# folder = Path(r"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_h")
# tif_files = list(folder.glob("*.tif"))
# logging.info(f"Found {len(tif_files)} TIFF files in {folder_new}")

# dst_crs = "EPSG:3035"
# dst_res = 2  # meters

# folder_new = Path(f"/home/admin_climatecharted_com/data/adb_po_pgra_2027_h_3035_{dst_res}m")
# folder_new.mkdir(exist_ok=True)  # create folder if it doesn't exist

# for idx, f in enumerate(tif_files):
#     out_file = folder_new / (f.stem + f"_3035_{dst_res}m.tif")
    
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
#             "nodata": -9999.0,  # <-- safe Float32 nodata,
#             "compress": "DEFLATE",  # optional compression
#             "tiled": True,           # recommended for large rasters
#             "predictor": 2           # improves compression for floats
#         })
        
#         with rasterio.open(out_file, "w", **kwargs) as dst:
#             for i in range(1, src.count + 1):
#                 reproject(
#                     source=rasterio.band(src, i),
#                     destination=rasterio.band(dst, i),
#                     src_transform=src.transform,
#                     src_crs=src.crs,
#                     dst_transform=transform,
#                     dst_crs=dst_crs,
#                     resampling=Resampling.bilinear,
#                     src_nodata=src.nodata,  # ensure nodata is handled
#                     dst_nodata=kwargs["nodata"]
#                 )
#     logging.info(f"[{idx+1}/{len(tif_files)}] Reprojected {f.name} -> {out_file.name}")         

# tif_files = list(folder_new.glob("*.tif"))
# logging.info(f"Found {len(tif_files)} TIFF files in {folder_new}")

# vrt_path = Path(r"/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_h_merged.vrt")

# gdal.BuildVRT(str(vrt_path), [str(f) for f in tif_files])
# logging.info(f"VRT built at {vrt_path}")

# out_3035 = Path(r"/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_h_merged_3035_2m.tif")
# gdal.Translate(
#     str(out_3035),
#     str(vrt_path),
#     creationOptions=[
#         "COMPRESS=DEFLATE",
#         "BIGTIFF=YES",
#         "TILED=YES",
#         "PREDICTOR=2"
#     ]
# )
# logging.info(f"1. Merged raster saved at: {out_3035}")

# out_4326 = Path(r"/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_h_merged_4326_2m.tif")
# gdal.Warp(
#     str(out_4326),
#     str(out_3035),        # source merged EPSG:3035 raster
#     dstSRS="EPSG:4326",
#     format="GTiff",
#     creationOptions=[
#         "COMPRESS=DEFLATE",
#         "BIGTIFF=YES",
#         "TILED=YES",
#         "PREDICTOR=2"
#     ]
# )
# logging.info(f"Merged raster saved in EPSG:4326 at {out_4326}")



# # m ==================================================================================================================

# folder = Path(r"/home/admin_climatecharted_com/data/Altezza/adb_po_pgra_2027_m")
# tif_files = list(folder.glob("*.tif"))

# dst_crs = "EPSG:3035"
# dst_res = 2  # meters

# folder_new = Path(f"/home/admin_climatecharted_com/data/adb_po_pgra_2027_m_3035_{dst_res}m")
# folder_new.mkdir(exist_ok=True)

# for idx, f in enumerate(tif_files):
#     out_file = folder_new / (f.stem + f"_3035_{dst_res}m.tif")
    
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
#             "nodata": -9999.0,  # <-- safe Float32 nodata,
#             "compress": "DEFLATE",  # optional compression
#             "tiled": True,           # recommended for large rasters
#             "predictor": 2           # improves compression for floats
#         })
        
#         with rasterio.open(out_file, "w", **kwargs) as dst:
#             for i in range(1, src.count + 1):
#                 reproject(
#                     source=rasterio.band(src, i),
#                     destination=rasterio.band(dst, i),
#                     src_transform=src.transform,
#                     src_crs=src.crs,
#                     dst_transform=transform,
#                     dst_crs=dst_crs,
#                     resampling=Resampling.bilinear,
#                     src_nodata=src.nodata,  # ensure nodata is handled
#                     dst_nodata=kwargs["nodata"]
#                 )
#     logging.info(f"[{idx+1}/{len(tif_files)}] Reprojected {f.name} -> {out_file.name}")

# tif_files = list(folder_new.glob("*.tif"))
# vrt_path = Path(r"/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_m_merged.vrt")

# gdal.BuildVRT(str(vrt_path), [str(f) for f in tif_files])
# logging.info(f"VRT built at {vrt_path}")

# out_3035  = Path(r"/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_m_merged_3035_2m.tif")
# gdal.Translate(
#     str(out_3035 ),
#     str(vrt_path),
#     creationOptions=[
#         "COMPRESS=DEFLATE",
#         "BIGTIFF=YES",
#         "TILED=YES",
#         "PREDICTOR=2"
#     ]
# )
# logging.info(f"2. Merged raster saved at: {out_3035 }")

# out_4326 = Path(r"/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_m_merged_4326_2m.tif")
# gdal.Warp(
#     str(out_4326),
#     str(out_3035),        # source merged EPSG:3035 raster
#     dstSRS="EPSG:4326",
#     format="GTiff",
#     creationOptions=[
#         "COMPRESS=DEFLATE",
#         "BIGTIFF=YES",
#         "TILED=YES",
#         "PREDICTOR=2"
#     ]
# )
# logging.info(f"Merged raster saved in EPSG:4326 at {out_4326}")