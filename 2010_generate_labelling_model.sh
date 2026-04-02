#!/bin/bash

rm -rf adaption/
mkdir -p adaptation

cp model_adaptation/dsb.yaml adaptation/
cp model_adaptation/mapAM.py adaptation/

cp generated/corpus_output/uasr_configurations/info/classes.txt adaptation/

cp db-hsb-asr/model/default/3_20.hmm                    adaptation/
cp db-hsb-asr/model/default/feainfo.object              adaptation/

pushd dLabPro
source bin/activate
cd ../adaptation

UASR_HOME="dummy" ./mapAM.py dsb.yaml

popd
