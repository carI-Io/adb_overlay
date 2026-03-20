#####################
# ADB po 2025 overlay
#####################

tmux new -s adb
cd /home/admin_climatecharted_com/GitHub/adb_flood && { time ./run.sh; } &> ./execution_output.txt

adb  ETA  
tmux kill-session -t adb

tmux ls
tmux attach -t adb

################################

tmux new -s adb
cd /home/admin_climatecharted_com/GitHub/adb_flood && { time ./run.sh; } &> ./execution_output.txt

adb  ETA  
tmux kill-session -t adb

tmux ls
tmux attach -t adb

################################

# make it executable
ls -l ./run.sh
chmod +x ./run.sh
ls -l ./run.sh

# or
bash ./run.sh

################################

git --version
git init
git add .
git commit -m "Initial commit with Dockerfiles and source code"
git branch -M main
git remote add origin git@github.com:carI-Io/cc-test-docker.git
git push -u origin main

