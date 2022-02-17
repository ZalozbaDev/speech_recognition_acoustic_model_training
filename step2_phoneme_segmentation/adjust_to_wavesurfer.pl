#!/usr/bin/perl -w

@filelist = `find output/ -name "*.lab" | grep -v wavesurfer`;

foreach (@filelist)
{
	# print "Modify $_";	
	$tmp = $_;
	chomp($tmp);
	
	$outfile = $tmp;
	$outfile =~ s/\.lab/_wavesurfer\.lab/;
	
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
}
