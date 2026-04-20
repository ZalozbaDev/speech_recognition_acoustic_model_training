#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Please supply model to evaluate!"
	echo "Example: ./4030_and_so_on.sh 0_0"
	exit -1
fi

MODELFILE=$1
EXTRA_ARGS=""

UASR_HOME="uasr" ./dLabPro/bin.release/dlabpro UASR/scripts/dlabpro/HMM.xtp evl uasr-data/db-hsb-asr/HSB-01/info/train.cfg -Puasr.am.model="$1" -v2 $EXTRA_ARGS


