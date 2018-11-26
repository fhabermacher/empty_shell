#!/bin/bash

PS1="$PS1"
set -eu

# check required tools
installTools=0
python3 pip --version 2> /dev/null || installTools=1
virtualenv --version 2> /dev/null || installTools=1
if [ $installTools -eq 1 ]; then
  TOOLS="python3-pip virtualenv"
  echo "Please provide password to install $TOOLS"
  sudo apt install $TOOLS
fi

sudo apt-get install python3-tk
sudo apt-get install libboost1.58-all

VENV=venv
virtualenv -p python3 "$VENV"
. "$VENV/bin/activate"
python3 -m pip install -r requirements.txt

set +eu

# TODO: adapt PS1
echo "Exuecuting shell in virtual enviroment"
exec $SHELL
