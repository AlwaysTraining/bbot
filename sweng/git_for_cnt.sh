#!/bin/bash
tag=master
repopath="https://github.com/AlwaysTraining/bbot.git"
full=

#parse the command line
while [ $# -gt 0 ]
do
    case "$1" in
        -t) tag="$2"; shift;;
        -r) repopath="$2"; shift;;
        -f) full="full";;
        --) shift; break;;
        *)
            echo "usage: $0 [-t tag] [-r repopath] [-f] 
-t TAG          : repo tag, or changelist id (master)
-r REPOPATH     : path to git repository  (https://github.com/AlwaysTraining/bbot.git)
-f              : Full Checkout (FALSE)"
            exit
    esac
    shift
done

if [ -z "$tag" ] ; then
    echo "Tag required"
    exit 1
fi



echo "Getting bbot ($tag) for counting purposes"
oldir=$(pwd)
cd /tmp
mkdir -p bbotcnt
cd bbotcnt
rm -rf bbot bbot_${tag}${full}
set -x
git clone $repopath
set +x
mv bbot bbot_${tag}${full}
cd bbot_${tag}${full}
set -x
git checkout $tag
set +x
cntdir=$(pwd)

if [ -z "$full" ] ; then
    echo Removing soft links
    find . -type l -exec rm -f {} \;
    echo Removing sweng files
    rm -rf sweng

    echo Removing text files
    find . -name "*.txt" -exec rm -f {} \;
    echo Removing test data files
    rm -rf test/var/log
    echo "Removing git files"
    rm -rf .git
fi
echo "Performing raw line count"
wc -l $(find . -type f) | tail -n 1
echo moving from counting location $cntdir to running location $oldir
mv $cntdir $oldir
