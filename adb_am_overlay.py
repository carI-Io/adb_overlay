import logging
logging.basicConfig(level=logging.INFO)
import geopandas as gpd
import networkx as nx
import pandas as pd

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

adb_am_2026_merge_file = r"/home/admin_climatecharted_com/data/ADB/adb_am_2026/ADB-AM_2026_merge_cum_prob_RP/ADB-AM_2026_merge_cum_prob_RP.shp"
gdf = gpd.read_file(adb_am_2026_merge_file)
logging.info("ADB AM - loaded gdf")

# -------------------------
# 2. DISSOLVE (order here is irrelevant logically, but cleaner)
# -------------------------
gdf_dissolved = dissolve_touching_by_rp(gdf)

# -------------------------
# 5. SAVE
# -------------------------
gdf_dissolved.to_file(r"/home/admin_climatecharted_com/data/ADB/adb_am_2026/ADB-AM_2026_merge_RP_overlay")

logging.info("ADB AM - Done")