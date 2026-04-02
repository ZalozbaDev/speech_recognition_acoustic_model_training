#!/bin/bash

# apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev

if ! [ -e Python-3.11.0.tgz ] ; then
	wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
fi

rm -rf Python-3.11.0
tar xvfz Python-3.11.0.tgz

cd Python-3.11.0 
./configure --enable-optimizations 
make -j8 
echo "============================="
echo "Now run: sudo make altinstall"

