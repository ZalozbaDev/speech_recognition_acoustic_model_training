#!/bin/bash

if [ "$#" -ne 2 ]; then
	echo "Please supply root folder and pattern for filelist!"
	echo "Example: ./0005_01_generate_filelist.sh inputs/recordings/sig/ BBAA/0001/"
	exit -1
fi

MY_FILELIST=$(pwd)/inputs/flists/dsb.flst

# create folder if it does not exist yet
mkdir -p $(pwd)/inputs/flists/

rm -f $MY_FILELIST

pushd $1

for i in $(find $2 -name "*.wav"); do
	echo $i
	echo $(echo $i | sed -e s/\.wav$//) >> $MY_FILELIST
done

popd
