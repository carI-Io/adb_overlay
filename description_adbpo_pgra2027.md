tmux new -s adbpo_pgra2027
cd /home/admin_climatecharted_com/GitHub/flood_maps && { time ./run_adbpo_pgra2027.sh; } &> ./execution_output_adbpo_pgra2027.txt

PGPASSWORD='pza!gud2ZMN_fxq9ycr' psql -h 91.98.183.177 -p 6432 -U climatecharted -d climatecharted_geo

export PGHOST=91.98.183.177
export PGDB=climatecharted_geo
export PGUSER=climatecharted
export PGPASSWORD='pza!gud2ZMN_fxq9ycr'
export PGPORT=6432

source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate postgis

cd /home/admin_climatecharted_com/GitHub/adb_overlay 
{
  echo "=== $(date) ==="
  time ./load_raster_chuncks.sh \
    /home/admin_climatecharted_com/data/Altezza/adbpo_pgra2027_l_merged_milano_tr500_3035_5m.tif \
    adbpo_pgra2027_l_merged_milano_tr500_3035_5m_vm \
    3035 \
    100x100
} &>> ./exec_load_raster.txt


ETA 
tmux kill-session -t adbpo_pgra2027

tmux ls
tmux attach -t adbpo_pgra2027

# how to verify permission =======
ls -l ./run_adbpo_pgra2027.sh
chmod +x ./run_adbpo_pgra2027.sh
ls -l ./run_adbpo_pgra2027.sh

# otherwise explicit run =========
bash ./run_adbpo_pgra2027.sh

# ================================

################################