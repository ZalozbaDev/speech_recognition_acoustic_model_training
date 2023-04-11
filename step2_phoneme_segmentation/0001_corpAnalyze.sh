#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Please supply corpus to check parameters!"
	echo "Example: ./corpAnalyze.sh ../resources/2020_study_lamp/"
	echo "Example: ./corpAnalyze.sh ../resources/gilles/"
	exit -1
fi

# Source directory with files to analyze
InDir=$1

TotalLengthAudio=0

find $InDir -regex '.*\.\(mp3\|wav\)' -type f -print0 | while read -d $'\0' input
do
  #echo $input
 	
  D=$(soxi -D $input)
  d=$(soxi -d $input)
  sample_rate=$(soxi -r $input)
  bit_sample=$(soxi -b $input)	
  channels=$(soxi -c $input)	
  encoding=$(soxi -e $input)	
  prms=$(sox $input -n stats 2> >(grep 'RMS Pk dB') | rev | cut -d ' ' -f 1 | rev)
  trms=$(sox $input -n stats 2> >(grep 'RMS Tr dB') | rev | cut -d ' ' -f 1 | rev)
  voladj=$(sox $input -n stat 2> >(grep 'Volume adjustment') | rev | cut -d ' ' -f 1 | rev)
  pcount=$(sox $input -n stats 2> >(grep 'Pk count') | rev | cut -d ' ' -f 1 | rev)
  flat=$(sox $input -n stats 2> >(grep 'Flat factor') | rev | cut -d ' ' -f 1 | rev)

  # compute overall length of all files found
  TotalLengthAudio=$(echo "$TotalLengthAudio + $D" | bc)
  
  recording_verdict="OK"
  recording_cause=""
  
  # hack. scale=0 only removes decimals if result is divided by 1
  SNR=$(echo "scale=0; ($prms - $trms) / 1" | bc)
  if (($SNR < 20)); then
  	  if (($SNR < 10)); then
  	  	  recording_cause=$recording_cause"S!"
  	  else
  	  	  recording_cause=$recording_cause"S"
  	  fi
  	  recording_verdict="W_"
  fi
  
  # volume adjustment multiplied by 100 to compare to integer
  goodvoladj=$(echo "scale=0; ($voladj *100) / 1" | bc)
  if (($goodvoladj < 105)); then
  	  recording_verdict="W_"
  	  recording_cause=$recording_cause"V"
  fi
  
  # flat factor multiplied by 1000 to compare to integer
  goodflat=$(echo "scale=0; ($flat *1000) / 1" | bc)
  if (($goodflat > 0)); then
  	  recording_verdict="W_"
  	  recording_cause=$recording_cause"F"
  fi
  
  # paranoia, should in theory always be an integer
  goodpcount=$(echo "scale=0; ($pcount) / 1" | bc)
  if (($goodpcount > 2)); then
  	  if (($goodpcount > 10)); then
  	  	  recording_cause=$recording_cause"P!"
  	  else
  	  	  recording_cause=$recording_cause"P"
  	  fi
  	  recording_verdict="W_"
  fi  	  
  
  # TODO need a nice way to get rid of the subshell behaviour of bash
  # see: http://mywiki.wooledge.org/BashFAQ/024
  # to print total length only after the loop is complete
  echo $recording_verdict$recording_cause':'$'\t'$input$'\t'$D$'\t'$d$'\t'$prms$'\t'$trms$'\t'$voladj$'\t'$pcount$'\t'$flat$'\t'$sample_rate$'\t'$bit_sample$'\t'$channels$'\t'$encoding$'\t'$TotalLengthAudio
done

#echo
#echo "Total audio length: $TotalLengthAudio seconds."
#echo
echo
echo "Legend"
echo "Filename <TAB> DurationSeconds <TAB> DurationsHHMMSS <TAB> RMS_peak/dB <TAB> RMS_through/dB <TAB> VolumeAdjustment <TAB> PeakCount <TAB> FlatFactor <TAB> Samplerate <TAB> BitsPerSample <TAB> Channels <TAB> Encoding <TAB> OverallDurationSeconds"
echo
echo "Parameter documentation (from website https://www.scrc.umanitoba.ca/doc/scrchelp/man/sox.html):"
echo "==============================================================================================="
echo
echo "RMS_peak/dB and RMS_through/dB:"
echo "-------------------------------"
echo "[Pk lev dB and RMS lev dB are standard peak and RMS level measured in dBFS.]"
echo "RMS Pk dB and RMS Tr dB are peak and trough values for RMS level measured over a short window (default 50ms)."
echo
echo "This script will warn you if SNR is below 20 (letter \"S\")."
echo
echo "VolumeAdjustment:"
echo "-----------------"
echo "The parameter to the vol effect which would make the audio as loud as possible without clipping."
echo "[Note: See the discussion on Clipping above for reasons why it is rarely a good idea actually to do this.]"
echo
echo "This script will warn you if volume adjustment factor is below 1.05 (letter \"V\")."
echo
echo "PeakCount and FlatFactor:"
echo "-------------------------"
echo "Flat factor is a measure of the flatness (i.e. consecutive samples with the same value) of the signal at its peak levels (i.e. either Min level, or Max level)."
echo "Pk count is the number of occasions (not the number of samples) that the signal attained either Min level, or Max level."
echo
echo "This script will warn you if flat factor is non-null (letter \"F\") or peak count is above 2 (letter \"P\") [although this one should also ideally be 0]."
echo
