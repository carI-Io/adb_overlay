#!/usr/bin/env bash
set -euo pipefail 

source "$HOME/miniforge3/etc/profile.d/conda.sh"

conda activate ccpy4
cd /home/admin_climatecharted_com/GitHub/adb_flood

python -m adb_am_overlay
gsutil -m cp -r "/home/admin_climatecharted_com/data/ADB/adb_am_2026/ADB-AM_2026_merge_RP_overlay" gs://cc-geodata-bucket/

python -m adb_as_overlay
gsutil -m cp -r "/home/admin_climatecharted_com/data/ADB/adb_as_2026/ADB-AS_2026_merge_RP_overlay" gs://cc-geodata-bucket/

python -m adb_ao_overlay
gsutil -m cp -r "/home/admin_climatecharted_com/data/ADB/adb_ao/ADB_AO_H_M_L" gs://cc-geodata-bucket/

python -m ispra_overlay
gsutil -m cp -r "/home/admin_climatecharted_com/data/ISPRA/HPH_Mosaicatura_ISPRA_2020_H_M_L" gs://cc-geodata-bucket/