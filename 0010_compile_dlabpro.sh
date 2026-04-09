#!/bin/bash

if ! [ -e dLabPro ] ; then
	git clone https://github.com/ZalozbaDev/dLabPro.git dLabPro
fi

# apt install -y g++ make git procps nano libreadline-dev portaudio19-dev

# compile C part
pushd dLabPro
git checkout 50a0237a2e297ee13e097e928b544a1b8cfc6a7b

# enable compile fix for newer distros
# git cherry-pick 297f1dc7a6b86a7ed786f845e93e327576e913ae

# hard-code python3.11 include paths
git cherry-pick c231d0fe9f46959a226cdc6a6829d755a95b4b8f
git cherry-pick 2f5a93d93c029787bffe642d44877cafebf0be2d

make -j8 -C programs/dlabpro RELEASE
popd

