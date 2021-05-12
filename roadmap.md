## Goal
Write scripts/a commandline tool for **as lossless as possible** conversion between .cha and .conllu files. 

## Formats of Interest

### CHAT
#### Annotation Scheme

* `@` marks metadata 
  * `@Languages`, `@Participants`, `@ID`, `@Comment`, `@Begin`, `@End`...
* `*` marks utterances
  * `*CHI:	they are fighting .`
* `%` marks tiers
  * `%mor`, `%gra`...
* `:` is usually followed by a tab instead of a space character

#### Things to notice

* Order of the comments

### CoNLL-U
#### Annotation Scheme
* `#` marks comments, e.g. `#sent_id`
* 10-column tab-separated format
  * `ID`: token index, starting from 1; for multi-word tokens could be a range; could be a decimal number (>0) for empty nodes
  * `FORM`: token
  * `LEMMA`:lemma/stem of token
  * `UPOS`: universal POS
  * `XPOS`: language-specific POS, `_` if not specified
  * `FEATS`: list of morphological features, separated by `|`
  * `HEAD`: head of the current token, `0` marks the root
  * `DEPREL`: universal dependency relation
  * `DEPS`: head-deprel pairs.
  * `MISC`: miscellaneous, other annotations pertaining to the current token
* 1 empty line in-between sentences
* 1 empty line at EoF
* no trailing whitespace at EoL
* no field should be left empty, `_` is the placeholder to go to
* fields other than FORM, LEMMA, and MISC must not contain space characters
* no format-level distinction is made for the rare cases where the FORM or LEMMA is the literal underscore `_`

## General Approach

### .cha to .conllu

1. extract utterances as sentences (Sentence)
2. deal with CHILDES annotation symbols (remove but info should be kept somewhere, like in `MISC` as first value)
3. saves metadata somewhere (incl. filename, headers for the file; speakers and timestamps for the utterances; token-level info goes into `MISC`)
4. retrieve morphological/grammatical information from the tiers `%mor` and `%gra` if they exist, save to Sentence and/or Token; copy tier directly to sentence comment?
5. Sentence should have Token, speaker, sent id, sentence-level comments...
6. generate CoNLL-U format, make sure the resulting file is well-formatted

### .conllu to .cha

1. parse .conllu file
2. retrieve metadata, create file using filename, write file header
3. go through the sentences, reconstruct utterances from **Token** up and tiers
4. `@End`

### adding new information

1. incorporate new information, such as dependency structure to a tier in CHAT files
2. add such a tier so that it can be converted to CoNLL-U deprels easily (wishful thinking?)

## Potential Pitfalls

### Tagset conversion
The tags used in CHAT `%gra` tier and in UD may not be one-to-one. Still need to think of a way to use the annotations. 
Make use of CoNLL-U tools to populate the layers in .cha files?
## Implementation

### Parsing Files

### Structuring Information 

### Modifying/Generating Files

### External Dependency Parser?

## References

CoNLL-U format: https://universaldependencies.org/format.html

A somewhat similar project: https://github.com/zoeyliu18/process_CHILDES

## Schedule

12 May: Creates a roadmap for the project.

**Deadline** ?
