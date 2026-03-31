tmux new -s adbpo_pgra_2027
cd /home/admin_climatecharted_com/GitHub && { time ./run_adbpo_h_pgra_2027.sh; } &> ./execution_output_pgra_2027.txt






ETA 
tmux kill-session -t adbpo_pgra_2027

tmux ls
tmux attach -t adbpo_pgra_2027

# how to verify permission =======
ls -l ./run_adbpo_h_pgra_2027.sh
chmod +x ./run_adbpo_h_pgra_2027.sh
ls -l ./run_adbpo_h_pgra_2027.sh

# otherwise explicit run =========
bash ./run_adbpo_h_pgra_2027.sh

# ================================

################################