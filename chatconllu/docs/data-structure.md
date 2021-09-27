# data structure

## Sentence

- `speaker`: participant 3-letter code
- `tiers` in order ['%mor', '%gra', '%exp', '%com', ...]  #
- `gra`
- `mor`
- `chat_sent`
- `clean`
- `comments`
- `sent_id`
- `toks`

Keep original %mor/%xmor and %gra as well for comparison

## Token

- `index`: index in normalised string
- `form`: 'clean' word form / punctuation symbol
- `lemma`: if possible from %mor/%xmor (mind cases like `beg|beg` !!)
- `upos`: {tagset}
- `xpos`: {tagset} (for now stores original MOR POS categories)
- `feats`: {feature set}
- `head`: int
- `deprel`: {deprel}
- `deps`: `head:deprel` pairs
- `misc`: --> any modifications/ extra info pertaining to this token
- `multi`: int
- `type`: clitics type
- `surface`: surface form (to remove)
