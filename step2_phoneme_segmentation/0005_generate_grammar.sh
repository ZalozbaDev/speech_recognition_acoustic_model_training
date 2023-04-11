#!/bin/bash

if [ "$#" -ne 3 ]; then
	echo "Please supply lexicon, labels and output file!"
	echo "Example: ./0005_generate_grammar.sh inputs/grammar/dsb_lex.txt inputs/recordings/trl/ inputs/grammar/dsb.grm"
	exit -1
fi

rm -f $3

export PERLINFILE=$1
export PERLOUTFILE=$3

perl -e '
# print "in=$ENV{PERLINFILE} and out=$ENV{PERLOUTFILE}!"; 
open (INHANDLE, "<:encoding(UTF-8)", "$ENV{PERLINFILE}") or die "Cannot open input file!";
open (OUTHANDLE, ">:encoding(UTF-8)", "$ENV{PERLOUTFILE}") or die "Cannot open output file!";
# binmode(STDOUT, "encoding(UTF-8)");
while (<INHANDLE>)
{
	$tmp = $_;
	($oneword,$phonetics) = $tmp =~ m/(.*)\t(.*)/;
	# print "$oneword --> $phonetics \n";
	$ucword=uc($oneword);
	printf OUTHANDLE "LEX: $ucword\t$phonetics\n";
	
}
close INHANDLE; 
close OUTHANDLE;
'

echo >> $3
echo >> $3

for i in $(find $2 -name "*.trl"); do
	echo -n $i" "
	
	echo -n "GRM: (S) " >> $3
	for k in $(cat $i); do
		ONEWORD=$(echo $k | sed -e 's/\r//g')
		
		echo -n "$ONEWORD:$ONEWORD "
		echo -n "$ONEWORD:$ONEWORD " >> $3
	done
	echo -n "(F)" >> $3
	
	echo
	echo >> $3
done
