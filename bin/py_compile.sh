#!/bin/bash

# Path to your own script
# http://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself
pushd . > /dev/null
SCRIPT_PATH="${BASH_SOURCE[0]}";
  while([ -h "${SCRIPT_PATH}" ]) do
    cd "`dirname "${SCRIPT_PATH}"`"
    SCRIPT_PATH="$(readlink "`basename "${SCRIPT_PATH}"`")";
  done
cd "`dirname "${SCRIPT_PATH}"`" > /dev/null
SCRIPT_PATH="`pwd`";
popd  > /dev/null

source $SCRIPT_PATH/devenv.rc

set -e

for i in $(find $bbot_ROOT -name "*.py") ; do
    echo "Checking Syntax: $i"
    python -m py_compile $i 
done

echo "No compile errors detected"



