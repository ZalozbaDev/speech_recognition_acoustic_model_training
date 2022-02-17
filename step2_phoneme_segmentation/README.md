# Automated phoneme segmentation

This step automates the process of adding phonetic labels to audio recordings. These are necessary to use the audio
recordings later for training of a (new) acoustic model. The data and adapted model from the previous step is used
for this purpose.

Inputs:

* adapted acoustic model ("hsb.hmm") and statistics ("feainfo.object") from step1
	* check & replace in directory inputs/model
* description of phonemes ("classes.txt")
    * check & replace in directory inputs/info
* word loop lexicon ("hsb.grm")
    * check & replace in directory inputs/grammar
* a list ("adptest.flst") of audio recordings and matching transcripts
    * check & replace list in directory inputs/flists
    * example audio data and transcripts can be found in "inputs/sig" and "inputs/trl"
        * audio files should be in wav format mono 16kHz
        * transcripts must match the word loop lexicon (check case!) and be one word per line
* config file ("label.cfg")
    * to be found in uasr-data/db-hsb-asr/HSB-01/info/

Configuration ("label.cfg"):

* Some file names and paths can be adjusted if needed.

Tools:

* dLabPro signal processing and acoustic pattern recognition toolbox
    * see https://github.com/ZalozbaDev/dLabPro
* UASR ("Unified Approach to signal Synthesis and Recognition") software and scripts
    * see https://github.com/ZalozbaDev/UASR

Running:

* Build the container using the supplied "Dockerfile"
    * see also inline comments
    
```console
docker build -t speech_recognition_acoustic_model_training_step2 .
```

Outputs:

* generated label files for every audio file in the list 
	* see "Dockerfile" on how to extract the files after successful container build

Evaluation:

* Results can be viewed using the "wavesurfer" tool (https://www.speech.kth.se/wavesurfer/).
    * Assure that the correct "snack" bindings for TCL are installed (e.g. libsnack-alsa)
    * The unmodified label files are one-off (start time instead of end time for phonemes is used).
    * Perl helper script "adjust_to_wavesurfer.pl" generates label files for use with wavesurfer.
        * Script uses hard coded "output" search path and writes new files with "_wavesurfer" appended.

