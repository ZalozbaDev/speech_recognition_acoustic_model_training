#!/bin/bash

if [ $# -lt 1 ]; then
	echo "Must specify model to evaluate!"
	echo "example: /run_evaluation.sh 3_8"
	exit;
fi

EXTRA_ARGS=""

if [ $# -eq 2 ]; then
	echo "2nd argument found - generate detailed label files!"
	EXTRA_ARGS=" -Puasr.am.eval.lab=TRUE "
fi

echo "Evaluating $1 - EXTRA_ARGS='${EXTRA_ARGS}'"

UASR_HOME="uasr" /dLabPro/bin.release/dlabpro UASR/scripts/dlabpro/HMM.xtp evl uasr-data/db-hsb-asr/HSB-01/info/train.cfg -Puasr.am.model="$1" -v2 $EXTRA_ARGS


