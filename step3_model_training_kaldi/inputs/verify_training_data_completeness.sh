#!/bin/bash

for i in $(find sig/ -name "*.wav"); do
	# echo $i;
	
	TRLFILE=$(echo $i | sed -e 's/sig\//trl\//' -e 's/\.wav/\.trl/')
	# echo $TRLFILE
	
	LABFILE=$(echo $i | sed -e 's/sig\//lab\//' -e 's/\.wav/\.lab/')
	# echo $LABFILE
	
	if ! [ -e "$TRLFILE" ] || ! [ -e "$LABFILE" ]; then
		echo -n "$i incomplete! "
		if ! [ -e "$TRLFILE" ]; then
			echo -n "No Transliterations! ";
		fi
		if ! [ -e "$LABFILE" ]; then
			echo -n "No Labels! ";
		fi
		echo
	#else
		# echo "$i OK!"
	fi
	
done
