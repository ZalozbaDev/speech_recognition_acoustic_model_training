#!/bin/bash

if ! [ -e dLabPro ] ; then
	git clone https://github.com/ZalozbaDev/dLabPro.git dLabPro
fi

# apt install -y g++ make git procps nano libreadline-dev portaudio19-dev

# compile C part
pushd dLabPro
git checkout 50a0237a2e297ee13e097e928b544a1b8cfc6a7b

# enable for newer distros
# git cherry-pick 297f1dc7a6b86a7ed786f845e93e327576e913ae

make -j8 -C programs/dlabpro RELEASE
popd

