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

### Parsing the files

### Storage of information

### Generating files

### Dependency Parser?

## References

CoNLL-U format: https://universaldependencies.org/format.html

https://github.com/zoeyliu18/process_CHILDES

## Schedule
