#!/usr/bin/env bash
set -euo pipefail 

source "$HOME/miniforge3/etc/profile.d/conda.sh"

conda activate ccpy4
cd /home/admin_climatecharted_com/GitHub/adb_flood

python -m adb_overlay

gsutil -m cp -r /home/admin_climatecharted_com/data/ADB/AA_pda2025_L_overlay2
gsutil -m cp -r /home/admin_climatecharted_com/data/ADB/AA_pda2025_M_overlay2