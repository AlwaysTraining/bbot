#!/bin/bash
logger "Starting bbots"
id="1FzFO8mnQDNYTRKiHYcLpoHOvqxZJClBVZLtVXyuteKI"
url="https://docs.google.com/feeds/download/documents/export/Export?id=$id&exportFormat=txt"
echo "Pulling Latest from source control"
cd $1
git pull
echo "Setting up python environment"
cd bin
source devenv.rc
curl -s $url > bbots.sh
dos2unix bbots.sh
chmod +x bbots.sh
./bbots.sh
logger "bbots Finished"
