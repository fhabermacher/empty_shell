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

# Make sure we're having similar gcc setup, to avoid error like "/usr/lib/x86_64-linux-gnu/libstdc++.so.6: version `GLIBCXX_3.4.22' not found"
#        Note, might be that first a "sudo apt-get upgrade libstdc++6" is required too; I shall check that.
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt-get update
sudo apt install gcc-6
sudo apt install g++-6
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-6 60 --slave /usr/bin/g++ g++ /usr/bin/g++-6

VENV=venv
virtualenv -p python3 "$VENV"
. "$VENV/bin/activate"
python3 -m pip install dash.ly --upgrade # Otherwise dash may not work despite it being in requirements.txt
python3 -m pip install -r requirements.txt

# Prepare for gunicorn. Cf. https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-16-04
sudo apt-get install python3-dev nginx # Though: Is python3-dev sth that really goes beyond std. python and thus is not anyways always there?
source venv/bin/activate
pip install gunicorn flask # Though: I reckon flask may be superfluous here as we're anyways using dash where it's kind of integrated already?

set +eu

# TODO: adapt PS1
echo "Exuecuting shell in virtual enviroment"
exec $SHELL
