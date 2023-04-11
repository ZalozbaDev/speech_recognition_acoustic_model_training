#!/bin/bash

if [ "$#" -lt 1 ]; then
        echo "Please supply corpus to listen to [and an optional directory-regex to select a folder]!"
        echo "Example: ./listen_and_verify_corpus.sh ../resources/myrepository/ [sig/SPEAKERID/0001/] [file_regex]"
        echo
        echo "Regex examples:"
        echo "\"*_[0-9].wav\"       : files from   0..9.wav"
        echo "\"*_[0-9][0-9].wav\"  : files from  00..99.wav (leading zero!!!)"
        echo "\"*_1[0-9][0-9].wav\" : files from 100..199.wav"
        echo "\"*_2[0-4][0-9].wav\" : files from 200..249.wav"
        exit -1
fi

PATTERN_TO_GREP="./"

REGEX="*.wav"

if [ "$#" -ge 2 ]; then
	PATTERN_TO_GREP="./"$2
	echo "Checking files in folder $PATTERN_TO_GREP only!"
fi

if [ "$#" -ge 3 ]; then
	REGEX=$3
	echo "Apply file regex $REGEX!"
fi

FIRST_FILE=""
SKIP_SUCCESSFUL=""

read -p "Na kotru dataju mam skočić? (ENTER = prěnja dataja): " FIRST_FILE

if [ "${#FIRST_FILE}" == "0" ]; then
	echo "Zapocnu z prenjej datajy!"
	SKIP_SUCCESSFUL=""
else
	echo "Pytam dataju kiz so konci na $FIRST_FILE"
	SKIP_SUCCESSFUL="FALSE"
fi

pushd $1
for i in $(find $PATTERN_TO_GREP -name $REGEX | sort); do
	TRLFILE=$(echo $i | sed -e s/\.wav/\.trl/ | sed -e "s/\.\/sig\//\.\/trl\//")
	if ! [ -e $TRLFILE ]; then
		echo "Transliterations file $TRLFILE to recording $i not found!"
		echo "ZMYLK!!! ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	else
		if [ "${#FIRST_FILE}" -gt "0" ]; then
			if [ "${#SKIP_SUCCESSFUL}" -gt "0" ]; then
				if [[ $i == *$FIRST_FILE ]]; then
					echo "Found $i!"
					SKIP_SUCCESSFUL=""
				fi
			fi
		fi
		

		if [ "${#SKIP_SUCCESSFUL}" == "0" ]; then

			REPEAT_PLAYING=1
			while [ "$REPEAT_PLAYING" == "1" ]
			do
				echo -n "$i: "
				cat $TRLFILE | tr '\n' ' '
				echo
				echo "================"
				aplay $i
				read -p "ENTER --> dale, pismik a ENTER --> wospjetować" KEYSPRESSED
				echo "================"
				echo "================"
			
				if [ "${#KEYSPRESSED}" == "0" ]; then
					REPEAT_PLAYING=0
				fi
			done
			
		else
			echo "Přeskoču $i"
		fi
	fi
done
