#!/bin/bash

#one argument must be passed, the maximum numnber of minutes to randomly sleep
echo "bbots cron job begins: $(date)"


# user passed in a number of minutes, get random number 
# between 0 and that number
SLEEPSECS=$(($1*60))
value=$(($RANDOM%$SLEEPSECS))
# Sleep for that time.
echo Sleeping for $(($value/60)) minutes
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
git commit -m "Automated checkin triggered by cron job"
git push
./bbots.sh
logger "Finished bbots"
echo "bbots Finished: $(date)"
