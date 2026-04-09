#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Please supply label to visualize!"
	echo "Example: ./3010_and_so_on.sh recordings/lab/SPEAKERID/SESSION/label.lab"
	exit -1
fi

LABELPATH=$1

perl convert_label_files.pl $1
