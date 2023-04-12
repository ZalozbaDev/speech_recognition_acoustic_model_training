#!/usr/bin/perl

my $NUM_ARGS = $#ARGV + 1;
if ($NUM_ARGS != 2)
{
	print("Must supply input and output file!\n");
	print("Example: TBD\n");
	exit;
}

my $input_file=$ARGV[0];
my $output_file=$ARGV[1];

open (READHANDLE, "$input_file") or die "Cannot open $input_file!\n";
open (WRITEHANDLE, "> $output_file") or die "Cannot open $output_file for writing!\n";

printf WRITEHANDLE "<table border=\"1\" style=\"width=100%%\"><tbody>\n";

while (<READHANDLE>)
{
	my $tmp = $_;
	chomp($tmp);
	
	my @fields = split " ", $tmp;
	
	printf WRITEHANDLE "<tr>\n";
	
	for ($i = 0; $i < @fields; $i++)
	{
		if ($i > 1) 
		{
			my $colorRed = $fields[$i];
			if ($colorRed > 255) { $colorRed = 255; }
			my $colorGreenBlue = 255 - $colorRed;
			# my $colorHexString = sprintf("%06X", ($colorRed * 0x10000) + ($colorGreenBlue * 0x100)  + $colorGreenBlue);
			my $colorHexString = sprintf("%06X", (255 * 0x10000) + ($colorGreenBlue * 0x100)  + $colorGreenBlue);
			printf WRITEHANDLE "<td style=\"background-color:#%s\">%s</td>", $colorHexString, $fields[$i];	
		}
		else
		{
			my $processedField = $fields[$i];
			if ($i == 1)
			{
				$processedField =~ s/://g;	
			}
			printf WRITEHANDLE "<td style=\"background-color:#FFFFFF\">%s</td>", $processedField;	
		}
	}
	printf WRITEHANDLE "</tr>\n";
}

printf WRITEHANDLE "</tbody>\n";

close READHANDLE;
close WRITEHANDLE;
