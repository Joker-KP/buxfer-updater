#!/bin/bash
echo "Buxfer update script"
source /home/joker/miniconda3/bin/activate web
cd ~/git/buxfer-updater/
python main.py

read -t 30 -N 1 -p "Will shutdown the computer in 30 secs. Continue (Y/n)?" answer
echo

if [[ "${answer,,}" == "n" ]]; then
  echo "Shutdown process stopped"
  sleep 5
else
  echo "Shutdown in progress..."
  sleep 2
  sudo shutdown -h now
fi
