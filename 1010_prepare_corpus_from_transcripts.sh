#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Please supply folder to search for trl files!"
	echo "Example: ./1010_and_so_on.sh recordings/trl/SPEAKERID/SESSION/"
	exit -1
fi

TRANSCRIPTPATH=$1

mkdir -p generated/corpus/

CORPUS_OUT=generated/corpus/dsb_from_transcripts.vocab

rm -f $CORPUS_OUT

for i in $(find $TRANSCRIPTPATH -name "*.trl"); do
	echo $i;
	sed -e 's/\(.*\)/\U\1/' -e 's/\xef\xbb\xbf//' $i >> $CORPUS_OUT
	echo -n " " >> $CORPUS_OUT
done

ls -l $CORPUS_OUT
