#!/bin/bash
echo "Starting bbots"
id="1FzFO8mnQDNYTRKiHYcLpoHOvqxZJClBVZLtVXyuteKI"
url="https://docs.google.com/feeds/download/documents/export/Export?id=$id&exportFormat=txt"
echo "Pulling Latest from source control"
cd $(dirname $0)
git pull
echo "Setting up python environment"
source devenv.rc
curl -s $url > bbots.sh
dos2unix bbots.sh
chmod +x bbots.sh
./bbots.sh
echo "bbots Finished"
