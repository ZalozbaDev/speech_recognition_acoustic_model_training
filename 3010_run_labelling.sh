#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Please supply folder to search for trl files!"
	echo "Example: ./3010_and_so_on.sh recordings/trl/SPEAKERID/SESSION/"
	exit -1
fi

TRANSCRIPTPATH=$1

# clean start
rm -rf uasr-data/
mkdir -p uasr-data/db-hsb-asr/HSB-01/flists uasr-data/db-hsb-asr/HSB-01/grammar uasr-data/db-hsb-asr/HSB-01/model uasr-data/db-hsb-asr/HSB-01/log uasr-data/db-hsb-asr/HSB-01/info

# generated files from corpus creation
cp generated/corpus_output/uasr_configurations/info/classes.txt uasr-data/db-hsb-asr/HSB-01/info/
cp generated/corpus_output/uasr_configurations/info/default.itp uasr-data/db-hsb-asr/HSB-01/info/

cp generated/corpus_output/uasr_configurations/grammar/dsb_phonetics.grm uasr-data/db-hsb-asr/HSB-01/grammar/

# generated labelling model
cp adaptation/dsb.hmm        uasr-data/db-hsb-asr/HSB-01/model/
cp adaptation/feainfo.object uasr-data/db-hsb-asr/HSB-01/model/

# generate file list and copy resources
TARGETSIGPATH=uasr-data/db-hsb-asr/common/sig
TARGETTRLPATH=uasr-data/db-hsb-asr/common/trl
TARGETLABPATH=uasr-data/db-hsb-asr/common/trl
mkdir -p ${TARGETSIGPATH}
mkdir -p ${TARGETTRLPATH}
mkdir -p ${TARGETLABPATH}

for i in $(find $TRANSCRIPTPATH -name "*.trl"); do
	echo $i;
	
	SOURCESIGNAL=$(echo $i | sed -e 's/\/trl\//\/sig\//' -e 's/\.trl/\.wav/')
	TARGETSIGNAL=${TARGETSIGPATH}/$(basename $i trl)wav
	TARGETTRANSCRIPT=${TARGETTRLPATH}/$(basename $i)
	FLISTENTRY=$(basename $i | sed -e 's/\.trl//')
	
	echo "SOURCESIGNAL:     ${SOURCESIGNAL}"
	echo "TARGETSIGNAL:     ${TARGETSIGNAL}"
	echo "TARGETTRANSCRIPT: ${TARGETTRANSCRIPT}"
	echo "FLISTENTRY:       ${FLISTENTRY}"
	
	# convert and copy wave file
	sox ${SOURCESIGNAL} -r 16000 -c 1 -b 16 ${TARGETSIGNAL}
	
	# convert and copy transcript
	sed -e 's/\(.*\)/\U\1/' -e 's/\xef\xbb\xbf//' $i > ${TARGETTRANSCRIPT}
	
	# add entry to filelist
	echo ${FLISTENTRY} >> uasr-data/db-hsb-asr/HSB-01/flists/dsb.flst
	
done

# copy config file
cp labelling_cfg/label.cfg uasr-data/db-hsb-asr/HSB-01/info/

UASR_HOME="uasr" ./dLabPro/bin.release/dlabpro UASR/scripts/dlabpro/HMM.xtp lab uasr-data/db-hsb-asr/HSB-01/info/label.cfg
