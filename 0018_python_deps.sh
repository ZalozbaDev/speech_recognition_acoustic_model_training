#!/bin/bash

# compile dlabpro python wrapper
pushd dLabPro
if ! [ -e bin/activate ] ; then
	python3.11 -m venv .
fi
source bin/activate

# export PYTHONPATH=$(pwd)/lib/

pip3.11 install numpy matplotlib pyyaml setuptools cython

pushd programs/python 
which python
which python3
which python3.11
./setup.py build 
# ./setup.py install 
# ./setup.py install --prefix ../../
./setup.py install --install-lib=../../lib/ --install-scripts=../../bin/
popd

popd

