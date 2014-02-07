#!/bin/bash
echo "bbots cron job begins: $(date)"

# Grab a random value between 0-3600
value=$(($RANDOM%3600))
# Sleep for that time.
echo Sleeping for $(($RANDOM%3600/60)) minutes
sleep $value

echo "Starting bbots: $(date)"

logger "Starting bbots"

id="1FzFO8mnQDNYTRKiHYcLpoHOvqxZJClBVZLtVXyuteKI"
url="https://docs.google.com/feeds/download/documents/export/Export?id=$id&exportFormat=txt"
echo "Pulling Latest code from source control"
cd $(dirname $0)
git pull
echo "Setting up python environment"
source devenv.rc
echo "Downloading latest commands from google docs"
curl -s $url > bbots.sh
dos2unix bbots.sh
chmod +x bbots.sh
echo "Adding latest file from google docs to source control"
git add .
git commit -m "Latest command file from google doc"
git push
./bbots.sh
logger "Finished bbots"
echo "bbots Finished: $(date)"
