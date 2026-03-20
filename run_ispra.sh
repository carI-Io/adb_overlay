#!/usr/bin/env bash
set -euo pipefail 

source "$HOME/miniforge3/etc/profile.d/conda.sh"

conda activate ccpy4
cd /home/admin_climatecharted_com/GitHub/adb_flood

python -m adb_clip

gsutil -m cp -r /home/admin_climatecharted_com/data/ADB/AA_pda2025_H_dissolved2 gs://cc-geodata-bucket/
gsutil -m cp -r /home/admin_climatecharted_com/data/ADB/AA_pda2025_M_overlay gs://cc-geodata-bucket/
gsutil -m cp -r /home/admin_climatecharted_com/data/ADB/AA_pda2025_L_overlay gs://cc-geodata-bucket/
gsutil -m cp -r /home/admin_climatecharted_com/data/ADB/AA_pda2025_H_M_L gs://cc-geodata-bucket/