# Acoustic model adaptation

This step uses an existing German acoustic model and re-uses / re-assigns German phoneme models to
the labels used for the new language. Besides using this adapted model directly for recognition, the
main use case here is to use it in a later step for phonetic labelling of recordings in the new langauge.

Inputs:

* existing German acoustic model (3_20.hmm) and statistics (feainfo.object)
    * see https://github.com/ZalozbaDev/db-hsb-asr/tree/main/model/default
* definition of phonemes (phonmap_v3.txt) and pronunciation rules (exceptions_v3.txt)
    * see https://github.com/ZalozbaDev/speech_recognition_corpus_creation/tree/main/examples/ex5/input
    * these will be used to generate the file "classes.txt" which is used for the adaptation
* config file (hsb.yaml)
    * the mappings must be in the same order as in the "classes.txt" file in order for the adaptation to work
    
Tools:

* dLabPro signal processing and acoustic pattern recognition toolbox
    * see https://github.com/ZalozbaDev/dLabPro
