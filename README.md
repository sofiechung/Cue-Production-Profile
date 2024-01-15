# Cue-Production-Profile
This package is an ongoing research project under the Speech Communications Group of MIT's Research Laboratory of Electronics department. The goal of this project is to develop an algorithm which characterizes context-based speech patterns as Cue Production Profiles.

The surface articulation of an underlying phoneme commonly fluctuates depending on the context. For instance, the associated acoustic cues for a /t/ phoneme produced at the beginning of an utterance may be distinct from the acoustic cues of a /t/ phoneme that is preceded and followed by a vowel. Thus, for an individual speaker or speaker group, we can investigate what specific phonemic contexts result in the associated acoustic cues to be produced. An algorithm has been developed which matches a target phoneme to its corresponding acoustic cues. For a given database, we can recover all of the contexts in which a phoneme was produced and tabulate the various acoustic cue production patterns that arose. Lastly, we label these patterns by their speech production type (e.g., standard production, flapping, etc.) and produce an output in the form of a Cue Production Profile. As a result, this profile would allow for the association of a set of acoustic cues in specific phonemic contexts for an individual speaker or speaker group, such as speakers from a specific dialect region. The algorithm can also be expanded to include prosodic cues to account for how stress and intonation can affect phoneme production.


# speech_ds.py
tl;dr: Creates a data structure of speech for a Praat TextGrid file.

This program takes as input a Praat TextGrid file that has been annotated with the spoken phrase, words, phonemes, and predicted and realized acoustic cues. Essentially, the algorithm will hierarchically organize this information and utilize Christine Soh's time-based alignment algorithm to match each acoustic cue to a phoneme. This provides insight on how a specified phoneme was produced in its context, and thus how part of the word was pronounced. 

# tabulate.py 
tl;dr: Given a phoneme, finds all contexts the phoneme appears in a directory of Praat TextGrid files. For each of these contexts, it extracts the associated acoustic cues and labels the speech production type accordingly. 

This program expands upon the work of Deborah Torres and Dora Hu. Given a directory of Praat TextGrid files, the progam utilizes speech_ds.py to match acoutic cues to phonemes. Then, with a user-specified phoneme, the program finds all instances of that phoneme across the directory and extracts each phonemic context and associated acoustic cues. Finally with this list of context-depdenent acoustic cues, the algorithm labels each entry by its speech production type if the produced acoustic cues warrants one. 
