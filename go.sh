#!/bin/bash

# You may start this script in terminal window on X session start.
# To achieve that in AntiX you may place the line below in ~/.desktop-session file:
# roxterm -e ~/path_to_buxsync/go.sh &

echo "BuxSync - transactions update script for manual accounts"
source ~/miniconda3/bin/activate web
cd ~/git/buxfer-updater/
python buxsync.py

# To be able to shutdown operating system without password prompt:
# - make sure your user is in sudoers group
# - place this line in the end of /etc/sudoers file: "my_username   ALL=(ALL) NOPASSWD: ALL"

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
