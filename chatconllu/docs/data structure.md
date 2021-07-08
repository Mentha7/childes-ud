# data structure

## :lemon: Meta
- handles lines starting with `@` in .cha files
- to .conllu: first n lines as is, begin with `#`
- back to .cha: remove `#`, use as is

## :lemon: Utterance (Sentence)

- sent_id  #
- participant code  #
- tiers in order ['%mor', '%gra', '%exp', '%com', ...]  #
- comments: tiers other than '%mor'/'%xmor', '%gra'  #
- normalised sentence string
- indexed tokens
- for now keep original %mor/%xmor and %gra as well for comparison

**Writer**

1. to .conllu: 
	- `#sent_id`
	- `#comments`
	- normalised sentence
	- tokens
	- empty line
2. to .cha: 
	- `*{participant code}:\t` utterance original form
	- `%{tier}:\t` tiers in order


## :lemon: Token

- conllu_id: index in normalised string
- conllu_word: 'clean' word form / punctuation symbol
- conllu_lemma: if possible from %mor/%xmor (mind cases like `beg|beg` !!)
- conllu_upos: {tagset} (for now keep it simple)
- conllu_xpos: {tagset} (for now keep it simple)
- conllu_feats: {feature set} (for now keep it simple)
- conllu_head: int
- conllu_deprel: {deprel}
- conllu_deps: `head:deprel` pairs
- conllu_misc: --> any modifications/ extra info pertaining to this token, next `[]` ?

**Writer**

1. to .conllu: write each token as a line (multiword token as span of multiple lines)
2. to .cha: restore token's surface form from `MISC`, piece together utterance and tiers




