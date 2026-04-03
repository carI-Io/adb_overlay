#!/usr/bin/env bash
set -euo pipefail 

source "$HOME/miniforge3/etc/profile.d/conda.sh"

conda activate ccpy4
cd /home/admin_climatecharted_com/GitHub/flood_maps

python -m adbpo_pgra2027_milano_check
# python -m adbpo_pgra2027
# python -m adbpo_pgra2027_milano_faster


# gsutil -m cp -r /home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_l_merged_milano_tr500_3035_5m.tif gs://cc-geodata-bucket/