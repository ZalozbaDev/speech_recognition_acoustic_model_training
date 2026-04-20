#!/bin/bash

# adjust here!
SPEAKERS_TRAIN=" BBAB BBAD BBAE "
SPEAKERS_TEST=" BBAG BBAH "

# clean start after labelling
rm -rf uasr-data/
mkdir -p uasr-data/db-hsb-asr/flists uasr-data/db-hsb-asr/grammar uasr-data/db-hsb-asr/log uasr-data/db-hsb-asr/info

# generated files from corpus creation
cp generated/corpus_output/uasr_configurations/info/classes.txt uasr-data/db-hsb-asr/info/
cp generated/corpus_output/uasr_configurations/info/default.itp uasr-data/db-hsb-asr/info/

# generate file lists and copy resources
TARGETSIGPATH=uasr-data/db-hsb-asr/common/sig
TARGETLABPATH=uasr-data/db-hsb-asr/common/lab

for SPEAKERS in ${SPEAKERS_TRAIN} ; do
	echo "Using Speaker ${SPEAKERS} for training!"
	
	
	for FILEENTRY in $(find recordings/lab/${SPEAKERS} -name "*.lab"); do
		echo $FILEENTRY
		
		SOURCESIGNAL=$(echo $FILEENTRY | sed -e 's/\/lab\//\/sig\//' -e 's/\.lab/\.wav/')
		TARGETSIGNAL=$(echo $SOURCESIGNAL | sed -e 's/recordings/uasr-data\/db-hsb-asr\/common/')
		
		TARGETLAB=$(echo $FILEENTRY | sed -e 's/recordings/uasr-data\/db-hsb-asr\/common/')
		FLISTENTRY=$(echo $TARGETSIGNAL | sed -e 's/\.wav//')

		mkdir -p $(dirname $TARGETSIGNAL)
		mkdir -p $(dirname $TARGETLAB)
		
		if [ -e ${SOURCESIGNAL} ]; then
		
			# echo "Copy + convert wav from ${SOURCESIGNAL} to ${TARGETSIGNAL}"
			
			# convert and copy wave file
			sox ${SOURCESIGNAL} -r 16000 -c 1 -b 16 ${TARGETSIGNAL}
		
			cp $FILEENTRY $(dirname $TARGETLAB)			
					
			# add entry to filelist
			echo ${FLISTENTRY} >> uasr-data/db-hsb-asr/flists/train.flst
		else
			echo "Skipping $FILEENTRY because required file ${SOURCESIGNAL} not found!"
		fi
		
	done
	
done

for SPEAKERS in ${SPEAKERS_TEST} ; do
	echo "Using Speaker ${SPEAKERS} for testing!"
	
	for FILEENTRY in $(find recordings/lab/${SPEAKERS} -name "*.lab"); do
		echo $FILEENTRY
		
		SOURCESIGNAL=$(echo $FILEENTRY | sed -e 's/\/lab\//\/sig\//' -e 's/\.lab/\.wav/')
		TARGETSIGNAL=$(echo $SOURCESIGNAL | sed -e 's/recordings/uasr-data\/db-hsb-asr\/common/')
		
		TARGETLAB=$(echo $FILEENTRY | sed -e 's/recordings/uasr-data\/db-hsb-asr\/common/')
		FLISTENTRY=$(echo $TARGETSIGNAL | sed -e 's/\.wav//')

		mkdir -p $(dirname $TARGETSIGNAL)
		mkdir -p $(dirname $TARGETLAB)
		
		if [ -e ${SOURCESIGNAL} ]; then
		
			# echo "Copy + convert wav from ${SOURCESIGNAL} to ${TARGETSIGNAL}"
			
			# convert and copy wave file
			sox ${SOURCESIGNAL} -r 16000 -c 1 -b 16 ${TARGETSIGNAL}
		
			cp $FILEENTRY $(dirname $TARGETLAB)			
					
			# add entry to filelist
			echo ${FLISTENTRY} >> uasr-data/db-hsb-asr/flists/test.flst
		else
			echo "Skipping $FILEENTRY because required file ${SOURCESIGNAL} not found!"
		fi
		
	done
	
done


