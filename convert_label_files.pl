#!/usr/bin/perl -w

$labfile=$ARGV[0];

$sigfile=$labfile;
# this will fail when path starts with "lab/"
$sigfile =~ s/\/lab\//\/sig\//;

print "Open $labfile and write $sigfile.\n";

open (INHANDLE, "$labfile") or die "Cannot open $labfile!\n";
open (OUTHANDLE, "> $sigfile") or die "Cannot open $sigfile!\n";

$ctr = 0;

$lastphoneme = ".";

while (<INHANDLE>)
{
	if ($ctr < 3)
	{
		$ctr++;	
		print OUTHANDLE $_;
	}
	else
	{
		($timestamp, $dummy, $currphoneme) = $_ =~ m/(.*) (121) (.*)$/;
		
		# print "$timestamp $dummy $currphoneme\n";
		
		printf OUTHANDLE "  %s %s %s\n", $timestamp, $dummy, $lastphoneme;
		
		$lastphoneme = $currphoneme;
	}
}

close INHANDLE;
close OUTHANDLE;

$sigfile =~ s/\.lab/\.wav/;

system("wavesurfer $sigfile");
