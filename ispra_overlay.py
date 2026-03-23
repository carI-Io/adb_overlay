import logging
logging.basicConfig(level=logging.INFO)
import geopandas as gpd
import networkx as nx
import pandas as pd

# Paths
layers = {
    "H": r"/home/admin_climatecharted_com/data/ISPRA/HPH_Mosaicatura_ISPRA_2020_premerge/HPH_Mosaicatura_ISPRA_2020_premerge.shp",
    "M": r"/home/admin_climatecharted_com/data/ISPRA/MPH_Mosaicatura_ISPRA_2020_premerge/MPH_Mosaicatura_ISPRA_2020_premerge.shp",
    "L": r"/home/admin_climatecharted_com/data/ISPRA/LPH_Mosaicatura_ISPRA_2020_premerge/LPH_Mosaicatura_ISPRA_2020_premerge.shp",
}

MIN_AREA = 0.25

def filter_valid_geoms(gdf):
    gdf["geometry"] = gdf.geometry.buffer(0)
    gdf = gdf[~gdf.geometry.is_empty]
    gdf = gdf[gdf.geometry.area > MIN_AREA]
    return gdf


def dissolve_touching_by_rp(gdf):
    gdf["geometry"] = gdf.geometry.buffer(0)

    result = []

    for rp_value, group in gdf.groupby("RP"):
        logging.info(f"RP {rp_value}")
        group = filter_valid_geoms(group).reset_index(drop=True)
        if len(group) == 0:
            continue

        sindex = group.sindex
        G = nx.Graph()

        for i, geom in enumerate(group.geometry):
            G.add_node(i)
            possible = list(sindex.intersection(geom.bounds))

            for j in possible:
                if i >= j:
                    continue

                if geom.touches(group.geometry[j]) or geom.intersects(group.geometry[j]):
                    G.add_edge(i, j)

        components = list(nx.connected_components(G))

        for comp in components:
            subset = group.loc[list(comp)]
            dissolved_geom = subset.union_all()

            row = subset.iloc[0].copy()
            row["geometry"] = dissolved_geom
            result.append(row)

    return gpd.GeoDataFrame(result, crs=gdf.crs)


# -------------------------
# 1. LOAD
# -------------------------
gdfs = {k: gpd.read_file(v) for k, v in layers.items()}
logging.info("ISPRA - loaded gdfs")

# -------------------------
# 2. DISSOLVE (order here is irrelevant logically, but cleaner)
# -------------------------
gdf_H_dissolved = gdfs["H"]
logging.info("ISPRA - gdf H dissolved")
gdf_M_dissolved = gdfs["M"]
logging.info("ISPRA - gdf M dissolved")
gdf_L_dissolved = gdfs["L"]
logging.info("ISPRA - gdf L dissolved")

# -------------------------
# 3. OVERLAY (hierarchy H > M > L)
# -------------------------

# Remove H from M
gdf_M_overlayed = gpd.overlay(gdf_M_dissolved, gdf_H_dissolved, how="difference")
logging.info("overlayed gdf_M")

# Remove M from L
gdf_L_overlayed = gpd.overlay(gdf_L_dissolved, gdf_M_dissolved, how="difference")
logging.info("overlayed gdf_L")

# -------------------------
# 4. MERGE FINAL LAYERS
# -------------------------
final_gdf = gpd.GeoDataFrame(
    pd.concat([
        gdf_H_dissolved,
        gdf_M_overlayed,
        gdf_L_overlayed
    ], ignore_index=True),
    crs=gdf_H_dissolved.crs
)

# -------------------------
# 5. SAVE
# -------------------------
gdf_M_overlayed.to_file(r"/home/admin_climatecharted_com/data/ISPRA/MPH_Mosaicatura_ISPRA_2020_overlay")
gdf_L_overlayed.to_file(r"/home/admin_climatecharted_com/data/ISPRA/LPH_Mosaicatura_ISPRA_2020_overlay")

final_gdf.to_file(r"/home/admin_climatecharted_com/data/ISPRA/HPH_Mosaicatura_ISPRA_2020_H_M_L")

logging.info("ISPRA - Done")