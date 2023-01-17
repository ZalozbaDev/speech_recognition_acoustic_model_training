# Audio augmentation

Clean speech recordings can be used for augmentation by introducing background noise with random levels, efectively doubling the available amount of speech data.

Augmentation provides larger amount of diverse speech data necessary for creation of robust triphone models.

Due to the possible changes in timing, labels of the original audio cannot be used. Augmented files need to be labelled
separately.

Inputs:

* files containing noise to be added
    * check folder inputs/noise
    * information about the origin of these files can be found in the same folder
* example audio files
    * check folder inputs/audio

Tools:

* Python script for augmenting files
    * check folder inputs/scripts
    
Running:

* Build the container using the supplied "Dockerfile"
    * see also inline comments
    
```console
docker build -t speech_recognition_acoustic_model_training_step1x5 .
```

Outputs:

* randomly augmented files
	* see "Dockerfile" on how to extract the files after successful container build
