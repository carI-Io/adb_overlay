import geopandas as gpd
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def process_adb(delim_gdf, gdfs, adb_name):

    MIN_AREA = 0.25  
    def filter_valid_geoms(gdf, min_area=MIN_AREA):
        gdf = gdf.copy()
        gdf["geometry"] = gdf.geometry.buffer(0)
        gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])]

        gdf = gdf[~gdf.geometry.is_empty]
        gdf = gdf[gdf.geometry.area > min_area]

        return gdf
    
    logging.info(f"Processing ADB: {adb_name}")

    # -------------------------
    # 1. CLIP + STANDARDIZE
    # -------------------------
    H = gpd.clip(gdfs["H"], delim_gdf)
    M = gpd.clip(gdfs["M"], delim_gdf)
    L = gpd.clip(gdfs["L"], delim_gdf)

    # Assign attributes
    H["RP"] = 20
    M["RP"] = 100
    L["RP"] = 200

    H["adb"] = adb_name
    M["adb"] = adb_name
    L["adb"] = adb_name

    # Keep only required columns
    H = H[["RP", "adb", "geometry"]]
    M = M[["RP", "adb", "geometry"]]
    L = L[["RP", "adb", "geometry"]]

    logging.info(f"1. {adb_name} clipped + standardized")

    # -------------------------
    # 2. M - H HIERARCHICAL OVERLAY
    # -------------------------

    M_clean = gpd.overlay(M, H, how="difference", keep_geom_type=False)
    logging.info(f"2. M_clean overlayed")

    HM = gpd.GeoDataFrame(
        pd.concat([H, M_clean], ignore_index=True),
        crs=H.crs
    )
    logging.info(f"2a. HM geom: {HM.geometry.type.unique()}")
    HM_valid = filter_valid_geoms(HM)
    logging.info(f"2b. HM_valid geom: {HM_valid.geometry.type.unique()}")

    # -------------------------
    # 3. L - (H + M) HIERARCHICAL OVERLAY
    # -------------------------

    L_clean = gpd.overlay(L, HM_valid, how="difference", keep_geom_type=False)
    logging.info(f"3. L_clean overlayed")

    logging.info(f"3a. L_clean geom: {L_clean.geometry.type.unique()}")
    L_valid = filter_valid_geoms(L_clean)
    logging.info(f"3b. L_valid geom: {L_valid.geometry.type.unique()}")

    
    # -------------------------
    # 4. FINAL MERGE
    # -------------------------
    final = gpd.GeoDataFrame(
        pd.concat([HM_valid, L_valid], ignore_index=True),
        crs=H.crs
    )

    # Enforce schema again (safety after overlay)
    final = final[["RP", "adb", "geometry"]]

    logging.info(f"4. {adb_name} merged")

    # -------------------------
    # 5. CLEAN GEOMETRIES
    # -------------------------

    # final = final.explode(index_parts=False) # Explode geometry collections (important)
    # final = final[
    #     final.geometry.type.isin(["Polygon", "MultiPolygon"])
    # ]
    # logging.info(f"{adb_name} geometry cleaned (polygon-only)")

    # final["geometry"] = final.buffer(0) # Optional but recommended: fix invalid geometries
    logging.info(f"5. {adb_name} processed")

    return final

logging.info(f"Start")

delim_adb_sa_file = r"/home/admin_climatecharted_com/data/ADB/delimitazione_distretto_ADB_Sardegna/delimitazione_distretto_ADB_Sardegna.shp"
delim_adb_si_file = r"/home/admin_climatecharted_com/data/ADB/delimitazione_distretto_ADB_Sicilia/delimitazione_distretto_ADB_Sicilia.shp"
delim_adb_ac_file = r"/home/admin_climatecharted_com/data/ADB/delimitazione_distretto_ADB_App_Centrale/delimitazione_distretto_ADB_App_Centrale.shp"

layers = {
    "H": r"/home/admin_climatecharted_com/data/ISPRA/HPH_Mosaicatura_ISPRA_2020_premerge/HPH_Mosaicatura_ISPRA_2020_premerge.shp",
    "M": r"/home/admin_climatecharted_com/data/ISPRA/MPH_Mosaicatura_ISPRA_2020_premerge/MPH_Mosaicatura_ISPRA_2020_premerge.shp",
    "L": r"/home/admin_climatecharted_com/data/ISPRA/LPH_Mosaicatura_ISPRA_2020_premerge/LPH_Mosaicatura_ISPRA_2020_premerge.shp",
}

gdfs = {k: gpd.read_file(v) for k, v in layers.items()}
logging.info("ISPRA - loaded gdfs")

delim_adb_sa = gpd.read_file(delim_adb_sa_file)
delim_adb_si = gpd.read_file(delim_adb_si_file)
delim_adb_ac = gpd.read_file(delim_adb_ac_file)

target_crs = gdfs["H"].crs

delim_adb_ac = delim_adb_ac.to_crs(target_crs)
delim_adb_si = delim_adb_si.to_crs(target_crs)
delim_adb_sa = delim_adb_sa.to_crs(target_crs)


gdf_si = process_adb(delim_adb_si, gdfs, "SI")
gdf_si.to_file(r"/home/admin_climatecharted_com/data/ADB/ispra_adbsi")
logging.info("SI stored\n")

gdf_sa = process_adb(delim_adb_sa, gdfs, "SA")
gdf_sa.to_file(r"/home/admin_climatecharted_com/data/ADB/ispra_adbsa")
logging.info("SA stored\n")

gdf_ac = process_adb(delim_adb_ac, gdfs, "AC")
gdf_ac.to_file(r"/home/admin_climatecharted_com/data/ADB/ispra_adbac")
logging.info("AC stored\n")

final_all = gpd.GeoDataFrame(
    pd.concat([gdf_ac, gdf_si, gdf_sa], ignore_index=True),
    crs=gdf_ac.crs
)
final_all.to_file(r"/home/admin_climatecharted_com/data/ADB/ispra_adb_ac_si_sa")
logging.info("ispra_adb_ac_si_sa stored\n")


adb_merged = gpd.read_file(r"/home/admin_climatecharted_com/data/ADB/ADB_merged")
final_ispra_adb = gpd.GeoDataFrame(
    pd.concat([adb_merged, final_all], ignore_index=True),
    crs=adb_merged.crs
)
output_file = r"/home/admin_climatecharted_com/data/ADB/ispra_adb_2026"
final_ispra_adb.to_file(output_file)
logging.info("ispra_adb_2026 stored")