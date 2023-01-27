#!/bin/bash

# check all provided data
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

# check data used by scripts
for i in $(find flists -name "*.flst"); do
	echo "Checking script $i";

	for k in $(cat $i); do
		# echo $k;
		
		SIGFILE="sig/"$k".wav"
		TRLFILE="trl/"$k".trl"
		LABFILE="lab/"$k".lab"
		
		if ! [ -e "$SIGFILE" ] || ! [ -e "$TRLFILE" ] || ! [ -e "$LABFILE" ]; then
			echo -n "$k incomplete! "
			if ! [ -e "$SIGFILE" ]; then
				echo -n "No Audio! ";
			fi
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
done
