# chatparser

## Progress

* :white_check_mark: Info in `%mor` and `%gra` needs to be associated to the correct tokens.
* :white_check_mark: Token structure, ideally each token writes to a line in conllu.
* Write a **well-formed** .conllu from .cha, test on multiple corpora:
    - :white_check_mark: no %gra and no %mor
    - :white_check_mark: only %gra
    - :white_check_mark: only %mor
    - :white_check_mark: both %gra and %mor
    - :white_check_mark: other dependent tiers where needed
        + :white_check_mark: can be written as sentence comments, e.g. `%com`, `%exp`

* Where to put headers in .conllu?
    - :white_check_mark: headers are currently put in the beginning of the conllu file as comments.

## Next Up


### Things to think about

* Write a **well-formed** .conllu from .cha, test on multiple corpora:
    - remaining issues:
        +  :fire: multi-word tokens' `form` is not there, currently using `lemma` instead
        + double-check the MOR-UPOS mapping
        + :fire: not all MOR codes are turned into UPOS tags
        + :fire: XPOS mapping to be added
        + :fire: deprels mapping to be added
        + :fire: :fire: :fire: can't get the right regex for
            + `*CHI:    < 结果 开 冰箱 > [<] < 就 > [//] 他 就 面包 拿 (.) 挤 好多 喔 [^c] .` -- **Chang2/BookReading/07.cha**

* How to store info in square brackets, e.g. `[+ IMIT]` so that they can be put back to their original position:
    - :fire: :fire: book keeping the process of utterance and token normalisation
        + utterance: sentence-level (need to remember position and info)
            * stores in previous Token.misc
            * store info in `MISC` field, use `|` as separator
        + token: transform clean form back to surface form
            * store surface form in `MISC` field


## Problems

### Grouping utterances with their dependent tiers

solved.



