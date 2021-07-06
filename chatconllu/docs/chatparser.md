# chatparser

```
list_files(dir)

read_file(filename)

parse_chat(filename)

normalise_utterance(line:str)

check_token(surface)

extract_token_info(clean:list, gra:list, mor: list)

create_sentence(idx, lines)

```


## Progress

* Info in `%mor` and `%gra` needs to be associated to the correct tokens.
* Token structure, ideally each token writes to a line in conllu.

## Next Up


### Things to think about:

* Write a **well-formed** .conllu from .cha, test on multiple corpora:
    - no %gra and no %mor
    - only %gra
    - only %mor
    - both %gra and %mor
    - other dependent tiers where needed
        + can be written as sentence comments, e.g. `%com`, `%exp`

* Where to put headers in .conllu?

* How to store info in square brackets, e.g. `[+ IMIT]` so that they can be put back to their original position:
    - book keeping the process of utterance and token normalisation
        + utterance: sentence-level (need to remember position and info)
            * stores in previous Token.misc
            * store info in `MISC` field, use `|` as separator
        + token: transform clean form back to surface form
            * store surface form in `MISC` field


## Problem

### Grouping utterances with their dependent tiers

From Brown corpus, `Eve/010600a.cha`:

Uncertain number of tiers, tier info associated with the utterance.
It would be best to handle each sentence with its own tiers, therefore group them into sentences. 
```
*MOT:   oh (.) ‡ I took it .
%mor:   co|oh beg|beg pro:sub|I v|take&PAST pro:per|it .
%gra:   1|0|BEG 2|1|BEGP 3|4|SUBJ 4|0|ROOT 5|4|OBJ 6|4|PUNCT
%com:   Fraser mentioned twice in conversation between Colin and Mother
*CHI:   Fraser . [+ IMIT]
%mor:   n:prop|Fraser .
%gra:   1|0|INCROOT 2|1|PUNCT
%com:   pronounces Fraser as fr&jdij .
*MOT:   I think that was Fraser .
%mor:   pro:sub|I v|think pro:dem|that cop|be&PAST&13S n:prop|Fraser .
%gra:   1|2|SUBJ 2|0|ROOT 3|4|SUBJ 4|2|COMP 5|4|PRED 6|2|PUNCT
```

#### Ugly Solution

Create a tmp file with each utterance separated by an empty line.

```
@xxx
@xxx

*MOT:   oh (.) ‡ I took it .
%mor:   co|oh beg|beg pro:sub|I v|take&PAST pro:per|it .
%gra:   1|0|BEG 2|1|BEGP 3|4|SUBJ 4|0|ROOT 5|4|OBJ 6|4|PUNCT
%com:   Fraser mentioned twice in conversation between Colin and Mother

*CHI:   Fraser . [+ IMIT]
%mor:   n:prop|Fraser .
%gra:   1|0|INCROOT 2|1|PUNCT
%com:   pronounces Fraser as fr&jdij .

*MOT:   I think that was Fraser .
%mor:   pro:sub|I v|think pro:dem|that cop|be&PAST&13S n:prop|Fraser .
%gra:   1|2|SUBJ 2|0|ROOT 3|4|SUBJ 4|2|COMP 5|4|PRED 6|2|PUNCT

@End

```



