# Acoustic model training

In this step, a new acoustic model is being trained from scratch, from the 
supplied labelled training data and the phoneme list.

Inputs:

* description of phonemes ("classes.txt") from step1
    * check & replace in directory inputs/info
* lists of audio recordings and matching labels for training ("train.flst") and evaluation ("test.flst")
    * check & replace list in directory inputs/flists
    * example audio data and labels (from step2) can be found in "inputs/sig" and "inputs/lab"
        * assure that no speaker is present in both lists!
        * use roughly 70% for training and 30% for evaluation
* config file ("train.cfg")
    * to be found in uasr-data/db-hsb-asr/HSB-01/info/

Configuration ("train.cfg"):

* Some file names and paths can be adjusted if needed.
* Adjust "uasr.am.train.split" to end training at a defined stage, otherwise training runs forever.

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

* generated models for each split ("X_Y.hmm") and statistics ("feainfo.object")
	* see "Dockerfile" on how to extract the files after successful container build

Evaluation:

