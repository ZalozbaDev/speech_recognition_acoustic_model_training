#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Please supply folder to convert wav files!"
	echo "Example: ./convert_wav.sh ../resources/gilles/sig/XXXX/YYYY"
	exit -1
fi

for i in $(find $1 -name "*.wav"); do
	echo $i;
	sox $i -r 16000 -c 1 -b 16 $i.proc.wav
	mv $i.proc.wav $i
done

