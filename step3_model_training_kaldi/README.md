# Acoustic model training

In this step, a new acoustic model is being trained from scratch, from the 
supplied labelled training data and the phoneme list.


Inputs:

* description of phonemes ("classes.txt")
    * check & replace in directory inputs/info
* phonetic lexicon ("hsb.lex")
    * check & replace in directory inputs/lexicon
* lists of audio recordings and matching transliterations+labels for training ("train.flst") and evaluation ("test.flst")
    * check & replace list in directory inputs/flists
    * a third list "dev.flst" is present for analysis purposes only
        * it could be used to find decoding parameters (weights) that could be independently evaluated
    * example audio data, transliterations and labels can be found in "inputs/sig", "inputs/trl" and "inputs/lab"
        * assure that no speaker is present in both training and test/dev lists!
        * although labels are not necessary for Kaldi itself, they are required for generation of the UASR compatible models

        
Configuration:

* UASR project as basis for conversion to Kaldi
    * check & replace in directory inputs/info
* Kaldi scripts
    * check & replace in directory inputs/kaldi_recipe
        * for small corpora, consider the following adjustments
            * hsb/s5/cmd.sh - "nJobs" and "nDecodeJobs" have been lowered
            * hsb/s5/run.sh - adjust parameter "OOV" on line 29 to provoke more or less words to be "out of vocabulary"
                * might be needed if your lexicon has much more entries than what is present in the corpus
    
                
Tools:

* dLabPro signal processing and acoustic pattern recognition toolbox
    * see https://github.com/ZalozbaDev/dLabPro
    * don't forget to build the Python wrapper!
* UASR ("Unified Approach to signal Synthesis and Recognition") software and scripts
    * see https://github.com/ZalozbaDev/UASR
* Kaldi
    * https://github.com/ZalozbaDev/kaldi.git
* conversion scripts to/from UASR
    * check & replace in directory inputs/scripts
    * "fea_uasr2kaldi.py" - set up a Kaldi project from a UASR project definition
    * "am_kaldi2uasr.py" - convert Kaldi acoustic models back to UASR format

    
Outputs:

* generated Kaldi and UASR models
	* see "Dockerfile" on how to extract the files after successful container build

	
Evaluation:

* results shown at the end of container build
    * see also Dockerfile how to show training results
    