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
        + :white_check_mark: can be written as sentence comments, e.g. `%com`, `%exp

## Next Up


### Things to think about

* Write a **well-formed** .conllu from .cha, test on multiple corpora:
    - remaining issues:
        + multi-word tokens' `form` is not there, currently using `lemma` instead
        + :fire: double-check the MOR-UPOS mapping
        + :fire: not all MOR codes are turned into UPOS tags
        + :fire: XPOS mapping to be added


## Problems

### Grouping utterances with their dependent tiers

solved.

### Clean utterances

- **Chang2/BookReading/07.cha**: can't get the right regex for:
    ```
    *CHI:    < 结果 开 冰箱 > [<] < 就 > [//] 他 就 面包 拿 (.) 挤 好多 喔 [^c] .
    ```
    solved.

### GR-deprel mappings

- dashed tokens
    ```
    tic-tac-toe  # used to have -tac and -toe as features...
    ```
- change head didn't work
    fixed.

### Organising metadata
- Complex cases of comments mixed with sentences with no tokens
    ignored for now.

