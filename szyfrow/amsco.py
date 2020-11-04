"""Enciphering and deciphering using the [Amsco cipher](http://ericbrandel.com/2016/10/09/the-amsco-cipher/). 
Also attempts to break messages that use an Amsco cipher.

The Amsco cipher is a column transpositoin cipher. The plaintext is laid out, 
row by row, into columns. However, different numbers of letters are laid out
in each cell, typically in a 1-2 pattern.

It's clearer with an example. Consider we're using the keyword "perceptive", 
which turns into "perctiv". The text ""It is a truth universally 
acknowledged, that a single man in, possession of a good fortune, must be in 
want of a wife." is laid out in seven columns like this:

    p  e  r  c  t  i  v
    --------------------
    i  ti s  at r  ut h 
    un i  ve r  sa l  ly 
    a  ck n  ow l  ed g 
    ed t  ha t  as i  ng 
    l  em a  ni n  po s 
    se s  si o  no f  ag 
    o  od f  or t  un e 
    mu s  tb e  in w  an 
    t  of a  wi f  e

The ciphertext is read out in columns, according to the order of the keyword.
In this example, the "c" column is read first, then the "e" column, and so on.
That gives the ciphertext of "atrowtnioorewi tiicktemsodsof utledipofunwe 
iunaedlseomut svenhaasiftba rsalasnnotinf hlygngsagean".
"""

from enum import Enum
import multiprocessing 
import itertools

from szyfrow.support.utilities import *
from szyfrow.support.language_models import *

__pdoc__ = {}

AmscoSlice = collections.namedtuple('AmscoSlice', ['index', 'start', 'end'])
__pdoc__['AmscoSlice'] = """Where each piece of plainatext ends up in the AMSCO 
transpositon cipher."""
__pdoc__['AmscoSlice.index'] = """Where the slice appears in the plaintext"""
__pdoc__['AmscoSlice.start'] = """Where the slice starts in the plaintext"""
__pdoc__['AmscoSlice.end'] = """Where the slice ends in the plaintext"""

class AmscoFillStyle(Enum):
    """Different methods of filling the grid.
    * `continuous`: continue the fillpattern unbroken by row boundaries
    * `same_each_row`: each row has the same fillpattern
    * `reverse_each_row`: each row has the reversed fillpattern to the row above
    """
    continuous = 1
    same_each_row = 2
    reverse_each_row = 3

def amsco_positions(message, keyword, 
      fillpattern=(1, 2),
      fillstyle=AmscoFillStyle.continuous,
      fillcolumnwise=False,
      emptycolumnwise=True):
    """Creates the grid for the AMSCO transposition cipher. Each element in the
    grid shows the index of that slice and the start and end positions of the
    plaintext that go to make it up.

    >>> amsco_positions(string.ascii_lowercase, 'freddy', \
        fillpattern=(1, 2)) # doctest:  +NORMALIZE_WHITESPACE
    [[AmscoSlice(index=3, start=4, end=6),
     AmscoSlice(index=2, start=3, end=4),
     AmscoSlice(index=0, start=0, end=1),
     AmscoSlice(index=1, start=1, end=3),
     AmscoSlice(index=4, start=6, end=7)],
    [AmscoSlice(index=8, start=12, end=13),
     AmscoSlice(index=7, start=10, end=12),
     AmscoSlice(index=5, start=7, end=9),
     AmscoSlice(index=6, start=9, end=10),
     AmscoSlice(index=9, start=13, end=15)],
    [AmscoSlice(index=13, start=19, end=21),
     AmscoSlice(index=12, start=18, end=19),
     AmscoSlice(index=10, start=15, end=16),
     AmscoSlice(index=11, start=16, end=18),
     AmscoSlice(index=14, start=21, end=22)],
    [AmscoSlice(index=18, start=27, end=28),
     AmscoSlice(index=17, start=25, end=27),
     AmscoSlice(index=15, start=22, end=24),
     AmscoSlice(index=16, start=24, end=25),
     AmscoSlice(index=19, start=28, end=30)]]
    """
    transpositions = transpositions_of(keyword)
    fill_iterator = itertools.cycle(fillpattern)
    indices = itertools.count()
    message_length = len(message)

    current_position = 0
    grid = []
    current_fillpattern = fillpattern
    while current_position < message_length:
        row = []
        if fillstyle == AmscoFillStyle.same_each_row:
            fill_iterator = itertools.cycle(fillpattern)
        if fillstyle == AmscoFillStyle.reverse_each_row:
            fill_iterator = itertools.cycle(current_fillpattern)
        for _ in range(len(transpositions)):
            index = next(indices)
            gap = next(fill_iterator)
            row += [AmscoSlice(index, current_position, current_position + gap)]
            current_position += gap
        grid += [row]
        if fillstyle == AmscoFillStyle.reverse_each_row:
            current_fillpattern = list(reversed(current_fillpattern))
    return [transpose(r, transpositions) for r in grid]

def amsco_encipher(message, keyword, 
    fillpattern=(1,2), fillstyle=AmscoFillStyle.reverse_each_row):
    """AMSCO transposition encipher.

    >>> amsco_encipher('hellothere', 'abc', fillpattern=(1, 2))
    'hoteelhler'
    >>> amsco_encipher('hellothere', 'abc', fillpattern=(2, 1))
    'hetelhelor'
    >>> amsco_encipher('hellothere', 'acb', fillpattern=(1, 2))
    'hotelerelh'
    >>> amsco_encipher('hellothere', 'acb', fillpattern=(2, 1))
    'hetelorlhe'
    >>> amsco_encipher('hereissometexttoencipher', 'encode')
    'etecstthhomoerereenisxip'
    >>> amsco_encipher('hereissometexttoencipher', 'cipher', fillpattern=(1, 2))
    'hetcsoeisterereipexthomn'
    >>> amsco_encipher('hereissometexttoencipher', 'cipher', fillpattern=(1, 2), fillstyle=AmscoFillStyle.continuous)
    'hecsoisttererteipexhomen'
    >>> amsco_encipher('hereissometexttoencipher', 'cipher', fillpattern=(2, 1))
    'heecisoosttrrtepeixhemen'
    >>> amsco_encipher('hereissometexttoencipher', 'cipher', fillpattern=(1, 3, 2))
    'hxtomephescieretoeisnter'
    >>> amsco_encipher('hereissometexttoencipher', 'cipher', fillpattern=(1, 3, 2), fillstyle=AmscoFillStyle.continuous)
    'hxomeiphscerettoisenteer'
    """
    grid = amsco_positions(message, keyword, 
        fillpattern=fillpattern, fillstyle=fillstyle)
    ct_as_grid = [[message[s.start:s.end] for s in r] for r in grid]
    return combine_every_nth(ct_as_grid)


def amsco_decipher(message, keyword, 
    fillpattern=(1,2), fillstyle=AmscoFillStyle.reverse_each_row):
    """AMSCO transposition decipher

    >>> amsco_decipher('hoteelhler', 'abc', fillpattern=(1, 2))
    'hellothere'
    >>> amsco_decipher('hetelhelor', 'abc', fillpattern=(2, 1))
    'hellothere'
    >>> amsco_decipher('hotelerelh', 'acb', fillpattern=(1, 2))
    'hellothere'
    >>> amsco_decipher('hetelorlhe', 'acb', fillpattern=(2, 1))
    'hellothere'
    >>> amsco_decipher('etecstthhomoerereenisxip', 'encode')
    'hereissometexttoencipher'
    >>> amsco_decipher('hetcsoeisterereipexthomn', 'cipher', fillpattern=(1, 2))
    'hereissometexttoencipher'
    >>> amsco_decipher('hecsoisttererteipexhomen', 'cipher', fillpattern=(1, 2), fillstyle=AmscoFillStyle.continuous)
    'hereissometexttoencipher'
    >>> amsco_decipher('heecisoosttrrtepeixhemen', 'cipher', fillpattern=(2, 1))
    'hereissometexttoencipher'
    >>> amsco_decipher('hxtomephescieretoeisnter', 'cipher', fillpattern=(1, 3, 2))
    'hereissometexttoencipher'
    >>> amsco_decipher('hxomeiphscerettoisenteer', 'cipher', fillpattern=(1, 3, 2), fillstyle=AmscoFillStyle.continuous)
    'hereissometexttoencipher'
    """

    grid = amsco_positions(message, keyword, 
        fillpattern=fillpattern, fillstyle=fillstyle)
    transposed_sections = [s for c in [l for l in zip(*grid)] for s in c]
    plaintext_list = [''] * len(transposed_sections)
    current_pos = 0
    for slice in transposed_sections:
        plaintext_list[slice.index] = message[current_pos:current_pos-slice.start+slice.end][:len(message[slice.start:slice.end])]
        current_pos += len(message[slice.start:slice.end])
    return cat(plaintext_list)


def amsco_break(message, translist=None, patterns = [(1, 2), (2, 1)],
                                  fillstyles = [AmscoFillStyle.continuous, 
                                                AmscoFillStyle.same_each_row, 
                                                AmscoFillStyle.reverse_each_row],
                                  fitness=Pbigrams, 
                                  chunksize=500):
    """Breaks an AMSCO transposition cipher using a dictionary and
    n-gram frequency analysis.

    If `translist` is not specified, use 
    [`szyfrow.support.langauge_models.transpositions`](support/language_models.html#szyfrow.support.language_models.transpositions).

    >>> amsco_break(amsco_encipher(sanitise( \
            "It is a truth universally acknowledged, that a single man in \
             possession of a good fortune, must be in want of a wife. However \
             little known the feelings or views of such a man may be on his \
             first entering a neighbourhood, this truth is so well fixed in \
             the minds of the surrounding families, that he is considered the \
             rightful property of some one or other of their daughters."), \
        'encipher'), \
        translist={(2, 0, 5, 3, 1, 4, 6): ['encipher'], \
                   (5, 0, 6, 1, 3, 4, 2): ['fourteen'], \
                   (6, 1, 0, 4, 5, 3, 2): ['keyword']}, \
        patterns=[(1, 2)]) # doctest: +ELLIPSIS
    (((2, 0, 5, 3, 1, 4, 6), (1, 2), <AmscoFillStyle.continuous: 1>), -709.4646722...)
    >>> amsco_break(amsco_encipher(sanitise( \
            "It is a truth universally acknowledged, that a single man in \
             possession of a good fortune, must be in want of a wife. However \
             little known the feelings or views of such a man may be on his \
             first entering a neighbourhood, this truth is so well fixed in \
             the minds of the surrounding families, that he is considered the \
             rightful property of some one or other of their daughters."), \
        'encipher', fillpattern=(2, 1)), \
        translist={(2, 0, 5, 3, 1, 4, 6): ['encipher'], \
                   (5, 0, 6, 1, 3, 4, 2): ['fourteen'], \
                   (6, 1, 0, 4, 5, 3, 2): ['keyword']}, \
        patterns=[(1, 2), (2, 1)], fitness=Ptrigrams) # doctest: +ELLIPSIS
    (((2, 0, 5, 3, 1, 4, 6), (2, 1), <AmscoFillStyle.continuous: 1>), -997.0129085...)
    """
    if translist is None:
        translist = transpositions
    
    with multiprocessing.Pool() as pool:
        helper_args = [(message, trans, pattern, fillstyle, fitness)
                       for trans in translist
                       for pattern in patterns
                       for fillstyle in fillstyles]
        # Gotcha: the helper function here needs to be defined at the top level
        #   (limitation of Pool.starmap)
        breaks = pool.starmap(amsco_break_worker, helper_args, chunksize) 
        return max(breaks, key=lambda k: k[1])

def amsco_break_worker(message, transposition,
        pattern, fillstyle, fitness):
    plaintext = amsco_decipher(message, transposition,
        fillpattern=pattern, fillstyle=fillstyle)
    fit = fitness(sanitise(plaintext))
    return (transposition, pattern, fillstyle), fit

if __name__ == "__main__":
    import doctest