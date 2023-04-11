#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Please supply folder to convert trl files!"
	echo "Example: ./convert_wav.sh ../resources/gilles/trl/XXXX/YYYY"
	exit -1
fi

for i in $(find $1 -name "*.trl"); do
	echo $i;
	sed -e 's/\(.*\)/\U\1/' $i > $i.proc.trl
	mv $i.proc.trl $i
done

