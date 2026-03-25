# it's okay

import logging
logging.basicConfig(level=logging.INFO)
import geopandas as gpd
import networkx as nx
import pandas as pd

# Paths
layers = {
    "H": r"/home/admin_climatecharted_com/data/ADB/adb_ao/Tiranti_TR30_HPH_premerge/Tiranti_TR30_HPH_premerge.shp",
    "M": r"/home/admin_climatecharted_com/data/ADB/adb_ao/Tiranti_TR100_MPH_premerge/Tiranti_TR100_MPH_premerge.shp",
    "L": r"/home/admin_climatecharted_com/data/ADB/adb_ao/Tiranti_TR300_LPH_premerge/Tiranti_TR300_LPH_premerge.shp",
}


# -------------------------
# 1. LOAD
# -------------------------
gdfs = {k: gpd.read_file(v) for k, v in layers.items()}
gdfs["H"]['RP'] = 30
gdfs["M"]['RP'] = 100
gdfs["L"]['RP'] = 300

logging.info("ADB AO - loaded gdfs")

# -------------------------
# 3. OVERLAY (hierarchy H > M > L)
# -------------------------

# Remove H from M
gdf_M_overlayed = gpd.overlay(gdfs["M"], gdfs["H"], how="difference")
logging.info("overlayed gdf_M")

gdf_H_M_gdf = gpd.GeoDataFrame(
    pd.concat([
        gdfs["H"],
        gdf_M_overlayed
    ], ignore_index=True),
    crs=gdfs["H"].crs
)

# Remove M from L
gdf_L_overlayed = gpd.overlay(gdfs["L"], gdf_H_M_gdf, how="difference")
logging.info("overlayed gdf_L")

# -------------------------
# 4. MERGE FINAL LAYERS
# -------------------------
final_gdf = gpd.GeoDataFrame(
    pd.concat([
        gdf_H_M_gdf,
        gdf_L_overlayed
    ], ignore_index=True),
    crs=gdf_H_M_gdf.crs
)

# -------------------------
# 5. SAVE
# -------------------------
gdf_M_overlayed.to_file(r"/home/admin_climatecharted_com/data/ADB/adb_ao/ADB_AO_MPH_overlay")
gdf_L_overlayed.to_file(r"/home/admin_climatecharted_com/data/ADB/adb_ao/ADB_AO_LPH_overlay")

final_gdf.to_file(r"/home/admin_climatecharted_com/data/ADB/adb_ao/ADB_AO_Tiranti")
logging.info("ADB_AO_Tiranti saved")