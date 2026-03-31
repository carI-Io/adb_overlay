#!/usr/bin/env bash
set -euo pipefail 

source "$HOME/miniforge3/etc/profile.d/conda.sh"

conda activate hydromt-sfincs-test
cd /home/admin_climatecharted_com/GitHub/

python -m adbpo_h_pgra_2027

gsutil -m cp -r /home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_max_3035_2m.tif gs://cc-geodata-bucket/