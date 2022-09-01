

#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home
# https://www.instructables.com/Raspberry-Pi-Launch-Python-script-on-startup/

cd /
cd home/pi/Desktop/GOOD_ARC168/
sudo pigpiod
python gbase.py