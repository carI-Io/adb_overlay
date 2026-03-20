# 15:11

import geopandas as gpd

gdf_H_dissolved = gpd.read_file("/home/admin_climatecharted_com/data/ADB/AA_pda2025_H_dissolved/AA_pda2025_H_dissolved.shp")
gdf_M_dissolved = gpd.read_file("/home/admin_climatecharted_com/data/ADB/AA_pda2025_M_dissolved/AA_pda2025_M_dissolved.shp")
gdf_L_dissolved = gpd.read_file("/home/admin_climatecharted_com/data/ADB/AA_pda2025_L_dissolved/AA_pda2025_L_dissolved.shp")

gdf_L_overlayed = gpd.overlay(gdf_L_dissolved, gdf_M_dissolved, how="difference")
print("overlayed gdf_L")
gdf_L_overlayed.to_file("/home/admin_climatecharted_com/data/ADB/AA_pda2025_L_overlay2")

gdf_M_overlayed = gpd.overlay(gdf_M_dissolved, gdf_H_dissolved, how="difference")
print("overlayed gdf_M")
gdf_M_overlayed.to_file("/home/admin_climatecharted_com/data/ADB/AA_pda2025_M_overlay2")