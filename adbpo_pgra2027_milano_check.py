import rasterio
import numpy as np

adbpo_path = "/home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_l_merged_3035_2m.tif"
milano_path = "/home/admin_climatecharted_com/data/Altezza/Milano_TR500_2m.tif"

with rasterio.open(adbpo_path) as adb, rasterio.open(milano_path) as mil:
    # Compare resolution
    print("Resolution ADBPO:", adb.res)
    print("Resolution Milano:", mil.res)

    # Compare transforms
    print("Transform ADBPO:", adb.transform)
    print("Transform Milano:", mil.transform)

    # Check grid alignment: difference of top-left coordinates divided by pixel size
    dx = (mil.bounds.left - adb.bounds.left) / adb.res[0]
    dy = (adb.bounds.top - mil.bounds.top) / abs(adb.res[1])  # note: y pixel size is negative
    print("Offset in pixels (x, y):", dx, dy)

    # Determine if offset is integer (perfect alignment)
    aligned = np.isclose(dx, round(dx)) and np.isclose(dy, round(dy))
    print("Grids perfectly aligned?", aligned)