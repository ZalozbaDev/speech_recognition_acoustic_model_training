# Automated phoneme segmentation

This step automates the process of adding phonetic labels to audio recordings. These are necessary to use the audio
recordings later for training of a (new) acoustic model. The data and adapted model from the previous step is used
for this purpose.

Preparations:

* check the acoustic properties of the recorded audio
    * example: ./0001_corpAnalyze.sh inputs/sig/BBAA/0001/ 
    * check the files that have warnings (can be false warnings)
* check that the recorded audio matches the transcription
    * example: ./0002_listen_and_verify_corpus.sh inputs/recordings/
    * recordings can have several words, but there is a maximum length of a sentence!
* check that recordings are in proper format:
    * example for conversion: ./0003_convert_wav.sh inputs/recordings/sig/BBAA/0001/
* check that transcripts are all upper case:
    * example for conversion: ./0004_convert_trl.sh inputs/recordings/trl/
* (re-)generate grammar file from lexicon:
    * example: ./0005_generate_grammar.sh inputs/grammar/dsb_lex.txt inputs/recordings/trl/ inputs/grammar/dsb.grm
    
Inputs:

* adapted acoustic model ("dsb.hmm") and statistics ("feainfo.object") from step1
	* check & replace in directory inputs/model
* description of phonemes ("classes.txt") from step1
    * check & replace in directory inputs/info
* phonetic lexicon ("dsb.grm")
    * check & replace in directory inputs/grammar
* a list ("dsb.flst") of audio recordings and matching transcripts
    * check & replace list in directory inputs/flists
    * example for autogeneration: (cd inputs/recordings/ && find . -name "*.wav" | sed -e "s/\.\/sig\///" -e "s/\.wav//") > inputs/flists/dsb.flst
    * example audio data and transcripts can be found in "inputs/recordings/sig" and "inputs/recordings/trl"
        * audio files should be in wav format mono 16kHz
        * transcripts must match the word loop lexicon (check case!) and be one word per line
	* please consult https://github.com/ZalozbaDev/speech_recognition_corpus_creation before creating own recordings!
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
* Sanity of labelling should be checked because long labels are rejected during training.
    * Check for warnings when running the "check_label_length.pl" script, and possibly exclude these recordings from training.
