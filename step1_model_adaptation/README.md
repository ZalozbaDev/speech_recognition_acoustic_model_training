# Acoustic model adaptation

This step uses an existing German acoustic model and re-uses / re-assigns German phoneme models to
the labels used for the new language. Besides using this adapted model directly for recognition, the
main use case here is to use it in a later step for phonetic labelling of recordings in the new langauge.

Inputs:

* existing German acoustic model ("3_20.hmm") and statistics ("feainfo.object")
    * see https://github.com/ZalozbaDev/db-hsb-asr/tree/main/model/default
* phonemes defintion file ("input/config/classes.txt")
    * there must be an 1:1 mapping of symbols to the conversion config file
* conversion config file ("input/config/dsb.yaml")
    * the mappings must be in the same order as in the "classes.txt" file in order for the adaptation to work

Configuration ("dsb.yaml"):

* Some file names can be adjusted if needed.
* Mapping in the same order (left-hand-side) as in the generated "classes.txt":
    * At the right-hand side, one or more phonemes of the existing German model will be specified.
    * If you specify more than one phoneme at the right-hand-side, they will be merged into one.
    * The list of phonemes of the German model can be found here:
        * https://zalozbadev.github.io/UASR/manual/index.html?reference/UasrPhonemeSets.html
        * https://github.com/ZalozbaDev/db-hsb-asr/blob/fdf61f4e22fa4eab521bfe26d89a54b2aacdeb44/common/info/classes.txt
    
Tools:

* dLabPro signal processing and acoustic pattern recognition toolbox
    * see https://github.com/ZalozbaDev/dLabPro
* "input/scripts/mapAM.py" script that performs the adaptation

Running:

* Build the container using the supplied "Dockerfile"
    * see also inline comments
    
```console
docker build -t speech_recognition_acoustic_model_training_step1 .
```

Outputs:

* adapted model "dsb.hmm" and (unmodified) "feainfo.object"

Evaluation:

* No direct evaluation possible.
