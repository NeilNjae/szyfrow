"""Descriptive models of a natural language (in this case, English).

The functions `Pwords`, `Pletters`, `Pbigrams`, and `Ptrigrams` return the 
log probability of a section of text.

If you want to use a different language, replace the data files in 
[`szyfrow/language_model_files`](../language_model_files/index.html).

* `count_1l.txt`: counts of single letters
* `count_2l.txt`: counts of pairs letters, bigrams
* `count_3l.txt`: counts of triples of letters, triagrams
* `words.txt`: a dictionary of words, used for keyword-based cipher breaking.
  These words should only contain characters cointained in 
  `string.ascii_letters`.

"""

import string
import random
import collections
import itertools
from math import log10
import os 
import importlib.resources as pkg_resources

import szyfrow.support.norms
from szyfrow.support.utilities import sanitise, deduplicate
from szyfrow import language_model_files


def datafile(name, sep='\t'):
    """Read key,value pairs from file.
    """
    with pkg_resources.open_text(language_model_files, name) as f:
    # with open(p name), 'r') as f:
        for line in f:
            splits = line.split(sep)
            yield [splits[0], int(splits[1])]

english_counts = collections.Counter(dict(datafile('count_1l.txt')))
"""Counts of single letters in English."""
normalised_english_counts = szyfrow.support.norms.normalise(english_counts)
"""Normalised counts of single letters in English (the sum of all counts
adds to 1)."""

english_bigram_counts = collections.Counter(dict(datafile('count_2l.txt')))
"""Counts of letter bigrams in English."""
normalised_english_bigram_counts = szyfrow.support.norms.normalise(english_bigram_counts)
"""Normalised counts of letter bigrams in English (the sum of all counts
adds to 1)."""

english_trigram_counts = collections.Counter(dict(datafile('count_3l.txt')))
"""Counts of letter trigrams in English."""
normalised_english_trigram_counts = szyfrow.support.norms.normalise(english_trigram_counts)
"""Normalised counts of letter trigrams in English (the sum of all counts
adds to 1)."""

keywords = []
"""A sample list of keywords, to act as a dictionary for 
dictionary-based cipher breaking attempts."""
with pkg_resources.open_text(language_model_files, 'words.txt') as f:
    keywords = [line.rstrip() for line in f]


def transpositions_of(keyword):
    """Finds the transpostions given by a keyword. For instance, the keyword
    'clever' rearranges to 'celrv', so the first column (0) stays first, the
    second column (1) moves to third, the third column (2) moves to second, 
    and so on.

    If passed a tuple, assume it's already a transposition and just return it.

    >>> transpositions_of('clever')
    (0, 2, 1, 4, 3)
    >>> transpositions_of('fred')
    (3, 2, 0, 1)
    >>> transpositions_of((3, 2, 0, 1))
    (3, 2, 0, 1)
    """
    if isinstance(keyword, tuple):
        return keyword
    else:
        key = deduplicate(keyword)
        transpositions = tuple(key.index(l) for l in sorted(key))
        return transpositions

transpositions = collections.defaultdict(list)
"""A sample dict of transpositions, to act as a dictionary for 
dictionary-based cipher breaking attempts. Each key is a transposition, 
each value is a list of words that give that transposition."""
for word in keywords:
    transpositions[transpositions_of(word)] += [word]


def weighted_choice(d):
    """Generate random item from a dictionary of item counts
    """
    delems, dweights = list(zip(*d.items()))
    return random.choices(delems, dweights)[0] 
    # target = random.uniform(0, sum(d.values()))
    # cuml = 0.0
    # for (l, p) in d.items():
    #     cuml += p
    #     if cuml > target:
    #         return l
    # return None

def random_english_letter():
    """Generate a random letter based on English letter counts
    """
    return weighted_choice(normalised_english_counts)


def ngrams(text, n):
    """Returns all n-grams of a text
    
    >>> ngrams(sanitise('the quick brown fox'), 2) # doctest: +NORMALIZE_WHITESPACE
    ['th', 'he', 'eq', 'qu', 'ui', 'ic', 'ck', 'kb', 'br', 'ro', 'ow', 'wn', 
     'nf', 'fo', 'ox']
    >>> ngrams(sanitise('the quick brown fox'), 4) # doctest: +NORMALIZE_WHITESPACE
    ['theq', 'hequ', 'equi', 'quic', 'uick', 'ickb', 'ckbr', 'kbro', 'brow', 
     'rown', 'ownf', 'wnfo', 'nfox']
    """
    return [text[i:i+n] for i in range(len(text)-n+1)]


class Pdist(dict):
    """A probability distribution estimated from counts in datafile.
    Values are stored and returned as log probabilities.
    """
    def __init__(self, data=[], estimate_of_missing=None):
        data1, data2 = itertools.tee(data)
        self.total = sum([d[1] for d in data1])
        for key, count in data2:
            self[key] = log10(count / self.total)
        self.estimate_of_missing = estimate_of_missing or (lambda k, N: 1./N)
    def __missing__(self, key):
        return self.estimate_of_missing(key, self.total)

def log_probability_of_unknown_word(key, N):
    """Estimate the probability of an unknown word.
    """
    return -log10(N * 10**((len(key) - 2) * 1.4))

Pw = Pdist(datafile('count_1w.txt'), log_probability_of_unknown_word)
"""A [Pdist](#szyfrow.support.language_models.Pdist) holding log probabilities 
of words. Unknown words have their probability estimated by 
[log_probability_of_unknown_word](#szyfrow.support.language_models.log_probability_of_unknown_word)"""
Pl = Pdist(datafile('count_1l.txt'), lambda _k, _N: 0)
"""A [Pdist](#szyfrow.support.language_models.Pdist) holding log probabilities 
of single letters. Unknown words have their probability estimated as zero."""
P2l = Pdist(datafile('count_2l.txt'), lambda _k, _N: 0)
"""A [Pdist](#szyfrow.support.language_models.Pdist) holding log probabilities 
of letter bigrams. Unknown words have their probability estimated as zero."""
P3l = Pdist(datafile('count_3l.txt'), lambda _k, _N: 0)
"""A [Pdist](#szyfrow.support.language_models.Pdist) holding log probabilities 
of letter trigrams. Unknown words have their probability estimated as zero."""

def Pwords(words): 
    """The Naive Bayes log probability of a sequence of words.
    """
    return sum(Pw[w.lower()] for w in words)

def Pletters(letters):
    """The Naive Bayes log probability of a sequence of letters.
    """
    return sum(Pl[l.lower()] for l in letters)

def Pbigrams(letters):
    """The Naive Bayes log probability of the bigrams formed from a sequence 
    of letters.
    """
    return sum(P2l[p] for p in ngrams(letters, 2))

def Ptrigrams(letters):
    """The Naive Bayes log probability of the trigrams formed from a sequence
    of letters.
    """
    return sum(P3l[p] for p in ngrams(letters, 3))


def cosine_distance_score(text):
    """Finds the dissimilarity of a text to English, using the cosine distance
    of the frequency distribution.

    >>> cosine_distance_score('abcabc') # doctest: +ELLIPSIS
    0.73771...
    """
    # return szyfrow.support.norms.cosine_distance(english_counts, 
    #     collections.Counter(sanitise(text)))
    return 1 - szyfrow.support.norms.cosine_similarity(english_counts, 
        collections.Counter(sanitise(text)))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
