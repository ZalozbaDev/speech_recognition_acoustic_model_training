#!/bin/bash

if ! [ -e UASR ] ; then
	git clone https://github.com/ZalozbaDev/UASR.git UASR
fi

pushd UASR
git checkout 8ff6eb727dc303fff4c5556574caa0dae204a3e6
popd

if ! [ -e db-hsb-asr ] ; then
	git clone https://github.com/ZalozbaDev/db-hsb-asr.git db-hsb-asr
fi

pushd db-hsb-asr
git checkout 8e86fb8171b58cc794e585433e4da7d2ea88a438
popd
