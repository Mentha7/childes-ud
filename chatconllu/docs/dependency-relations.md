# dependency relations

## GRASP - Syntactic Dependency Analysis Grammatical Relations 

#### **Predicate-Head Relations**

1. Subject: `SUBJ` --> `nsubj`
2. Clausal Subject: `CSUBJ` --> `csubj`
    - e. g. `That Eric cried moved Bush.` 
3. Object: `OBJ` --> `obj`
4. Object2: `OBJ2` : second/indirect object --> `iobj`
5. `IOBJ`  --> `iobj`
6. Complement: `COMP`: identifies clausal complement of a verb  --> `ccomp`
7. Predicate: `PRED` --> `xcomp` or change tree structure 
8. Clausal Prepositional Object: `CPOBJ`
9. Clausal Object: `COBJ`
10. Prepositional Object: `POBJ`
11. Serial: `SRL`: serial verbs  -> `xcomp`
    - e. g. `go play` , `come see`

#### **Argument-Head Relations**

1. Adjunct: `JCT` --> `advmod`, ...
2. Clausal Conjunct: `CJCT`  --> `advcl`
3. X Adjunct: `XJCT` --> `advcl`
4. Nominal Adjunct: `NJCT`  --> ``
5. Modifier: `MOD` --> `nmod`
6. Post Modifier: `POSTMOD` --> `amod`/`xcomp`
7. Possessive : `POSS`  --> `case`
8. Appositive: `APP`  --> `appos`
9. Clausal Modifier: `CMOD`  --> `ccomp`
10. X Modifier: `XMOD` --> `acl`
11. Determiner: `DET` --> `det`
12. Quantifier: `QUANT` --> `det`; if numbers `nummod`
13. Post Quantifier: `PQ` --> `det`
14. Auxiliary: `AUX` --> `aux`
15. Negation: `NEG` --> `advmod`, `Polarity=Neg`
16. Infinitive: `INF`: infinitive particle (`to`)
17. Link: `LINK`  --> `mark`
    - e. g. Wait **until** the noodles are cool.
18. Tag: `TAG`: tag question  --> `parataxis`
    - e. g. You know how to swim, **don't you?**

#### **Extra-Clausal Elements**
1. Communicator: `COM`  --> `discourse`
    - e. g. `hey`, `okay`...
2. Begin: `BEG`: initial clause-external element.  --> `vocative`
    - e. g. vocative, topic ...
3. End: `END` : sentence-final particles, single word tags `right?` --> `parataxis`
4. Incomplete Root: `INCROOT` : usual `ROOT` missing.  --> `root`, might need to change tree structure
5. Omission: `OM` --> `discourse:omission`

#### **Cosmetic Relations**
1. Punctuation: `PUNCT` --> `punct`
2. Local Punctuation: `LP`  --> `punct`
3. `BEGP`: Telation between  mark and `BEG`  --> `punct`
4. `ENDP`: Gelation between mark and `END`.  --> `punct`
5. `ROOT` --> `root`
    
#### **Series Relations**
1. Name: `NAME` --> `flat`
2. Date: `DATE`  --> `flat`
3. Enumeration: `ENUM`  --> `conj`
4. Conjunction: `CONJ`  --> `conj` but different structure
5. Coordination: `COORD`  --> `cc`
