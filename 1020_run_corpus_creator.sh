#!/bin/bash

rm -rf generated/corpus_output/

pushd dLabPro
source bin/activate
python3 ../corpus_creation/tooling/corpus_creator.py ../corpus_creation/configuration/DSB.yaml
popd

ls -lR generated/corpus_output/uasr_configurations/

echo "!!!!!!!!!!!!!! Removed lines from corpus !!!!!!!!!!!!!!!!!"

cat generated/corpus_output/corpus/dsb_phonetics.rmvd

echo "!!!!!!!!!!!!!! Removed lines from corpus !!!!!!!!!!!!!!!!!"
