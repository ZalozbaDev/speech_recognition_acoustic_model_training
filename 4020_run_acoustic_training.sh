#!/bin/bash

rm -f uasr-data/db-hsb-asr/HSB-01/info/train.cfg
cp training_cfg/train.cfg uasr-data/db-hsb-asr/HSB-01/info/

TIMESTAMP=$(date +%Y%m%d-%H%M%S)

UASR_HOME="uasr" ./dLabPro/bin.release/dlabpro UASR/scripts/dlabpro/HMM.xtp trn uasr-data/db-hsb-asr/HSB-01/info/train.cfg 2>&1 | tee logfile_${TIMESTAMP}.log

