tmux new -s adbpo_pgra2027
cd /home/admin_climatecharted_com/GitHub/flood_maps && { time ./run_adbpo_pgra2027.sh; } &> ./execution_output_adbpo_pgra2027.txt


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