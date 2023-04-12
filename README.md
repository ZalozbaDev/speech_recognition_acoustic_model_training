# English

## Acoustic model generation

This procedure allows to generate acoustic models for speech recognition from scratch. The following steps need to be
performed (see directory content for details):

* step1_model_adaptation
* step2_phoneme_segmentation
* step3_model_training_UASR

Documentation which was used to generate these examples can be found in the "report" folder.

## Authors

- Dr. Ivan Kraljevski (Fraunhofer Institute for Ceramic Technologies and Systems IKTS, Dresden, Germany)

- Dr. Frank Duckhorn (Fraunhofer Institute for Ceramic Technologies and Systems IKTS, Dresden, Germany)

- Daniel Sobe (Foundation for the Sorbian people)

## License

See file "LICENSE".

# Deutsch

## Training des akustischen Modells

Mit dieser Herangehensweise können akustische Modelle für die Spracherkennung von Grund auf erstellt werden. 
Die folgenden Schritte müssen durchgeführt werden (siehe README.md in den jeweiligen Verzeichnissen):

* step1_model_adaptation
    * Ein auf die Erkennung von Phonemen der deutschen Sprache trainiertes akustisches Modell wird derart "umgeschrieben",
      dass es für die Markierung von Phonemen in Sprachaufnahmen verwendet werden kann. Dabei können andere Symbole
      für Phoneme verwendet werden, und es können mehrere existierende Phonemmodelle zu einem neuen Modell zusammengefasst
      werden.
      
* step2_phoneme_segmentation
    * Das angepasste Modell wird verwendet, um in Sprachaufnahmen die aufgetretenen Phoneme zu markieren. Dazu werden die
      Transkriptionen in alle möglichen Varianten von Phonemen umgewandelt und die wahrscheinlichste Variante gewählt.
      
* step3_model_training_UASR
    * Die Sprachaufnahmen mit den markierten Phonemen werden dazu verwendet, ein leeres akustisches Modell zu trainieren.

Die Anleitung, mit deren Hilfe die Beispiele erzeugt wurden, befindet sich im Verzeichnis "report".

## Authoren

- Dr. Ivan Kraljevski (Fraunhofer Institut für keramische Technologien und Systeme IKTS, Dresden, Deutschland)

- Dr. Frank Duckhorn (Fraunhofer Institut für keramische Technologien und Systeme IKTS, Dresden, Deutschland)

- Daniel Sobe (Stiftung für das sorbische Volk)

## Lizenz

Siehe Datei "LICENSE".

