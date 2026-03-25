import logging
logging.basicConfig(level=logging.INFO)
import geopandas as gpd
import networkx as nx
import pandas as pd
from tqdm import tqdm

# Paths
layers = {
    "H": r"/home/admin_climatecharted_com/data/ISPRA/HPH_Mosaicatura_ISPRA_2020_premerge/HPH_Mosaicatura_ISPRA_2020_premerge.shp",
    "M": r"/home/admin_climatecharted_com/data/ISPRA/MPH_Mosaicatura_ISPRA_2020_premerge/MPH_Mosaicatura_ISPRA_2020_premerge.shp",
    "L": r"/home/admin_climatecharted_com/data/ISPRA/LPH_Mosaicatura_ISPRA_2020_premerge/LPH_Mosaicatura_ISPRA_2020_premerge.shp",
}

# -------------------------
# 1. LOAD
# -------------------------
gdfs = {k: gpd.read_file(v) for k, v in layers.items()}
gdfs = {k: gdf.buffer(0) for k, gdf in gdfs.items()}
logging.info("ISPRA - loaded gdfs")

# -------------------------
# 3. OVERLAY (hierarchy H > M > L)
# -------------------------

# Remove H from M
# gdf_M_overlayed = gpd.overlay(gdfs["M"], gdfs["H"], how="difference")


def fast_difference(A, B):
    # spatial index
    sindex = B.sindex

    result = []
    # for idx, geom in A.geometry.items():
    for idx, geom in tqdm(A.geometry.items(), total=len(A)):
    
        possible = list(sindex.intersection(geom.bounds))
        if not possible:
            result.append(geom)
        else:
            diff_geom = geom
            for j in possible:
                diff_geom = diff_geom.difference(B.geometry.iloc[j])
                if diff_geom.is_empty:
                    break
            if not diff_geom.is_empty:
                result.append(diff_geom)

    return gpd.GeoDataFrame(geometry=result, crs=A.crs)
gdf_M_overlayed = fast_difference(gdfs["M"], gdfs["H"])


gdf_M_overlayed.to_file(r"/home/admin_climatecharted_com/data/ISPRA/MPH_Mosaicatura_ISPRA_2020_overlay")
logging.info("overlayed gdf_M")

gdfs_H_M = gpd.GeoDataFrame(
    pd.concat([
        gdfs["H"],
        gdf_M_overlayed
    ], ignore_index=True),
    crs=gdfs["H"].crs
)

# Remove M from L
# gdf_L_overlayed = gpd.overlay(gdfs["L"], gdfs_H_M, how="difference")
gdf_L_overlayed = fast_difference(gdfs["L"], gdfs_H_M)
gdf_L_overlayed.to_file(r"/home/admin_climatecharted_com/data/ISPRA/LPH_Mosaicatura_ISPRA_2020_overlay")
logging.info("overlayed gdf_L")

# -------------------------
# 4. MERGE FINAL LAYERS
# -------------------------
final_gdf = gpd.GeoDataFrame(
    pd.concat([
        gdfs["H"],
        gdf_M_overlayed,
        gdf_L_overlayed
    ], ignore_index=True),
    crs=gdfs["H"].crs
)
final_gdf.to_file(r"/home/admin_climatecharted_com/data/ISPRA/HPH_Mosaicatura_ISPRA_2020_H_M_L")

logging.info("ISPRA - Done")