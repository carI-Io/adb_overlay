#!/usr/bin/env bash
set -euo pipefail 

source "$HOME/miniforge3/etc/profile.d/conda.sh"

conda activate ccpy4
cd /home/admin_climatecharted_com/GitHub/flood_maps

python -m adbpo_pgra2027_milano

gsutil -m cp -r /home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_l_merged_milano_tr500_3035_2m.tif gs://cc-geodata-bucket/