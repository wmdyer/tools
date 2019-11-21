# tools

## projective.py
A script that reads in a Universal Dependencies conllu file and reports number of non-projective sentences and words. Projectivity defined such that every word *w* which appears between a head *h* and dependent *d* must be dominated by *h* to be considered projective (cf. Marcus, 1965).

```
$ python projective.py ../UD_English-GUM/en_gum-ud-train.conllu
[====================] 100% N 66180/66180

non-projective
 sents: 0.0731 260/3557
 words: 0.0178 1177/66101
```
