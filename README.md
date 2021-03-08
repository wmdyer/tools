# tools

## projective.py
A script that reads in a Universal Dependencies conllu file and reports number of non-projective sentences and words. Projectivity defined such that every word *w* which appears between a head *h* and dependent *d* must be dominated by *h* to be considered projective (Marcus, 1965).

```
$ python projective.py ../UD_English-GUM/en_gum-ud-train.conllu
[====================] 100% N 66180/66180

non-projective
 sents: 0.0731 260/3557
 words: 0.0178 1177/66101
```

## extract_adj_triples.py
A script that extracts sequential triples of two adjectives and a noun from a conllu file. Triples are extracted according to the following criteria:
1. triple must be composed of one noun and two adjectives dependent on the noun
1. the adjectives cannot have dependents of their own
1. the noun can have other dependents, but other than compounds, other dependents cannot come between the noun and adjectives in the surface order
1. adjectives must have UPOS of 'ADJ' and be in an 'amod' dependency relation
1. adjective cannot be superlatives, comparatives, or ordinal numbers

```
usage: extract_adj_triples.py [-h] -i INFILE [INFILE ...] [-o OUTFILE]

extract triples from conllu file(s) according to rules above, outputting as:
"<word>/<POS>,<word>/<POS>,<word>/POS[TAB]<source>.conllu"

required arguments:
  -i, --infile    one or more input files in conllu format
  
optional arguments:
  -o, --outfile   name of file for outputting triples, default triples.csv
```
