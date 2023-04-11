#!/usr/bin/perl -w

@filelist = `find output/ -name "*.lab"`;

$biggestdiff = 0;
$biggestfile = "";

foreach (@filelist)
{
	# print "Modify $_";	
	$tmp = $_;
	chomp($tmp);
	
	# print "Open $tmp.\n";
	
	open (INHANDLE, "$tmp") or die "Cannot open $tmp!\n";
	
	$ctr = 0;

	# $lastphoneme = ".";
	$lasttimestamp = 0;
	
	while (<INHANDLE>)
	{
		if ($ctr < 3)
		{
			$ctr++;	
			# print OUTHANDLE $_;
		}
		else
		{
			my $dummy;
			my $currphoneme;
			
			($timestamp, $dummy, $currphoneme) = $_ =~ m/(.*) (121) (.*)$/;
			
			# print "$timestamp $dummy $currphoneme\n";
			
			# printf OUTHANDLE "  %s %s %s\n", $timestamp, $dummy, $lastphoneme;

			$diff = $timestamp - $lasttimestamp;
			
			if ($diff > 6.5)
			{
				printf "WARN: $tmp: Big timestamp diff found (%.2fs)!\n", $diff;	
			}
			
			if ($diff > $biggestdiff)
			{
				# printf "INFO: $tmp: New biggest timestamp diff in label set (%.2fs).\n", $diff;
				$biggestdiff = $diff;
				$biggestfile = $tmp;
			}
			
			$lasttimestamp = $timestamp;
		}
	}
	
	close INHANDLE;
}

printf "INFO: $biggestfile: Biggest timestamp diff in label set (%.2fs).\n", $biggestdiff;
