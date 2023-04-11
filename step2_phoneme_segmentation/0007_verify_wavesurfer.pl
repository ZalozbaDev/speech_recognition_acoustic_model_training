#!/usr/bin/perl -w

@filelist = `find output/ -name "*.lab"`;

foreach (@filelist)
{
	# print "Modify $_";	
	$tmp = $_;
	chomp($tmp);
	
	$outfile = $tmp;

	# this will fail when path starts with "lab/"
	$outfile =~ s/\/lab\//\/sig\//;

	$outfile =~ s/output\//inputs\/recordings\//;
	
	print "Open $tmp and write $outfile.\n";
	
	open (INHANDLE, "$tmp") or die "Cannot open $tmp!\n";
	open (OUTHANDLE, "> $outfile") or die "Cannot open $outfile!\n";
	
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
	
	$sigfile = $outfile;
	$sigfile =~ s/\.lab/\.wav/;
	
	system("wavesurfer $sigfile");
	
	system("rm $outfile");
	
	print "Press <Enter> for next file.";
	my $inputline = <STDIN>;
}
