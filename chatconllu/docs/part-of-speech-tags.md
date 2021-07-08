# part-of-speech tags

The part-of-speech codes used by the MOR program are different from UPOS of Universal Dependencies. 

## :grapes: comparison

|**UPOS**|**MOR POS Code**                          |**Notes**|
|:------:|:-----------------------------------------|:--------|
|ADJ    |`adj`, `adj:pred`                          |         |
|ADP    |`post`, `prep`                             |         |
|ADV    |`adv`, `adv:tem`                           |         |
|AUX    |`aux`                                      |         |
|CCONJ  |`coord`                                    |         |
|DET    |`qn`, `det:poss`, `det:art`, `det:dem`, `det:int`, `det:num`|`qn`: quantifier|
|INTJ   |`co`                                       |`co`: communicator|
|NOUN   |`n`, `n:let`, `n:pt`, `on`                 |         |
|NUM    |`num`                                      |         |
|PART   |`part`, `inf`                              |         |
|PRON   |`pro:dem`, `pro:exist`, `pro:indef`, `pro:int`, `pro:obj`, `pro:per`, `pro:poss`, `pro:refl`, `pro:rel`, `pro:sub`         |         |
|PROPN  |`n:prop`                                   |         |
|PUNCT  |                                           |*punctuations* are kept as symbols|
|SCONJ  |`conj`, `comp`                             |conjunction, complementizer|
|SYM    |                                           |         |
|VERB   |`v`, `cop`, `mod`                   |         |
|X      |                                           |         |

There are still some %mor codes left:

- :fire: `fil`: filler  --> INTJ?
- :fire: `neg`: negations/negative --> ADV?

## :grapes: references

- [Universal POS tags](https://universaldependencies.org/u/pos/index.html)
- [MOR POS Codes](https://talkbank.org/manuals/MOR.html#_Toc65933283)
