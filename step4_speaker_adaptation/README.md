# Model adaptation

The acoustic models can be adapted to fixed conditions for improved performance. In case
the application is operated withion constant acoustic conditions (speaker, microphone), the
general purpose model can be adjusted to these conditions.

For this purpose, recordings of sentences within these conditions need to be created. Labelling
is not necessary, but transcription must be provided.

Inputs:

* description of phonemes ("classes.txt") from step1
    * check & replace in directory inputs/info
* lists of audio recordings and matching labels for adaptation ("adptrain.flst") and optional evaluation ("adptest.flst")
    * check & replace list in directory inputs/flists
    * example audio data, transcriptions and labels can be found in "inputs/sig", "inputs/trl" and "inputs/lab"
        * "RECS/0001" contains mandatory adaptation data
        * "RECS/0003" contains optional evaluation data
        * labels for "RECS/0003" are only required for evaluation
* lexicon "hsb_small_sampa.ulex"
    * check & replace in directory inputs/lexicon
* trained acoustic model ("X_Y.hmm") and statistics ("feainfo.object") from step1
	* check & replace in directory inputs/model
* config files ("adapt.cfg" and "eval.cfg")
    * to be found in uasr-data/db-hsb-asr/HSB-01/info/

Configuration ("adapt.cfg" and "eval.cfg"):

* Some file names and paths can be adjusted if needed.
* Adjust the model to adapt in "uasr.am.model"
    * Alternatively use a cmdline override (see Dockerfile).

Tools:

* dLabPro signal processing and acoustic pattern recognition toolbox
    * see https://github.com/ZalozbaDev/dLabPro
* UASR ("Unified Approach to signal Synthesis and Recognition") software and scripts
    * see https://github.com/ZalozbaDev/UASR

Running:

* Build the container using the supplied "Dockerfile"
    * see also inline comments
    
```console
docker build -t speech_recognition_acoustic_model_training_step4 .
```

Outputs:

* adapted model ("X_Y_A.hmm") and statistics ("feainfo.object")
	* see "Dockerfile" on how to extract the files after successful container build

Evaluation:

* Evaluation is done as part of container creation:
    * First "before/after" evaluation is a too-optimistic one using a lexicon
    * Another "before/after" evaluation is then executed with free phoneme recognition (more realistic)
* Parameters to check and compare "before/after":
    * Label sequences:
        * Correctness
        * Accuracy
* In the provided example, only the free phoneme evaluation generates useful results:
    * Correctness improves ~ 12%
    * Accuracy improves ~ 20%
