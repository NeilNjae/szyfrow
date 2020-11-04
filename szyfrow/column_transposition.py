"""Enciphering and deciphering using the [Column transposition cipher](https://en.wikipedia.org/wiki/Bifid_cipher). 
Also attempts to break messages that use a column transpositon cipher.

A grid is layed out, with one column for each distinct letter in the keyword.
The grid is filled by the plaintext, one letter per cell, either in rows or
columns. The columns are rearranged so the keyword's letters are in alphabetical
order, then the ciphertext is read from the rearranged grid, either in rows
or columns. 

The Scytale cipher is a column cipher with an identity transposition, where the 
message is written in rows and read in columns. 

Messages that do not fill the grid are padded with fillvalue. Note that 
`szyfrow.support.utilities.pad` allows a callable, so that the message can be 
padded by random letters, for instance by calling 
`szyfrow.support.language_models.random_english_letter`.
"""

import math
import multiprocessing 
from itertools import chain
from szyfrow.support.utilities import *
from szyfrow.support.language_models import *

def column_transposition_encipher(message, keyword, fillvalue=' ', 
      fillcolumnwise=False,
      emptycolumnwise=False):
    """Enciphers using the column transposition cipher.
    Message is padded to allow all rows to be the same length.

    >>> column_transposition_encipher('hellothere', 'abcdef', fillcolumnwise=True)
    'hlohr eltee '
    >>> column_transposition_encipher('hellothere', 'abcdef', fillcolumnwise=True, emptycolumnwise=True)
    'hellothere  '
    >>> column_transposition_encipher('hellothere', 'abcdef')
    'hellothere  '
    >>> column_transposition_encipher('hellothere', 'abcde')
    'hellothere'
    >>> column_transposition_encipher('hellothere', 'abcde', fillcolumnwise=True, emptycolumnwise=True)
    'hellothere'
    >>> column_transposition_encipher('hellothere', 'abcde', fillcolumnwise=True, emptycolumnwise=False)
    'hlohreltee'
    >>> column_transposition_encipher('hellothere', 'abcde', fillcolumnwise=False, emptycolumnwise=True)
    'htehlelroe'
    >>> column_transposition_encipher('hellothere', 'abcde', fillcolumnwise=False, emptycolumnwise=False)
    'hellothere'
    >>> column_transposition_encipher('hellothere', 'clever', fillcolumnwise=True, emptycolumnwise=True)
    'heotllrehe'
    >>> column_transposition_encipher('hellothere', 'clever', fillcolumnwise=True, emptycolumnwise=False)
    'holrhetlee'
    >>> column_transposition_encipher('hellothere', 'clever', fillcolumnwise=False, emptycolumnwise=True)
    'htleehoelr'
    >>> column_transposition_encipher('hellothere', 'clever', fillcolumnwise=False, emptycolumnwise=False)
    'hleolteher'
    >>> column_transposition_encipher('hellothere', 'cleverly')
    'hleolthre e '
    >>> column_transposition_encipher('hellothere', 'cleverly', fillvalue='!')
    'hleolthre!e!'
    >>> column_transposition_encipher('hellothere', 'cleverly', fillvalue=lambda: '*')
    'hleolthre*e*'
    """
    transpositions = transpositions_of(keyword)
    message += pad(len(message), len(transpositions), fillvalue)
    if fillcolumnwise:
        rows = every_nth(message, len(message) // len(transpositions))
    else:
        rows = chunks(message, len(transpositions))
    transposed = [transpose(r, transpositions) for r in rows]
    if emptycolumnwise:
        return combine_every_nth(transposed)
    else:
        return cat(chain(*transposed))

def column_transposition_decipher(message, keyword, fillvalue=' ', 
      fillcolumnwise=False,
      emptycolumnwise=False):
    """Deciphers using the column transposition cipher.
    Message is padded to allow all rows to be the same length.

    Note that `fillcolumnwise` and `emptycolumnwise` refer to how the message
    is enciphered. To decipher a message, the operations are performed as an 
    inverse-empty, then inverse-transposition, then inverse-fill.

    >>> column_transposition_decipher('hellothere', 'abcde', fillcolumnwise=True, emptycolumnwise=True)
    'hellothere'
    >>> column_transposition_decipher('hlohreltee', 'abcde', fillcolumnwise=True, emptycolumnwise=False)
    'hellothere'
    >>> column_transposition_decipher('htehlelroe', 'abcde', fillcolumnwise=False, emptycolumnwise=True)
    'hellothere'
    >>> column_transposition_decipher('hellothere', 'abcde', fillcolumnwise=False, emptycolumnwise=False)
    'hellothere'
    >>> column_transposition_decipher('heotllrehe', 'clever', fillcolumnwise=True, emptycolumnwise=True)
    'hellothere'
    >>> column_transposition_decipher('holrhetlee', 'clever', fillcolumnwise=True, emptycolumnwise=False)
    'hellothere'
    >>> column_transposition_decipher('htleehoelr', 'clever', fillcolumnwise=False, emptycolumnwise=True)
    'hellothere'
    >>> column_transposition_decipher('hleolteher', 'clever', fillcolumnwise=False, emptycolumnwise=False)
    'hellothere'
    """
    transpositions = transpositions_of(keyword)
    message += pad(len(message), len(transpositions), fillvalue)
    if emptycolumnwise:
        rows = every_nth(message, len(message) // len(transpositions))
    else:
        rows = chunks(message, len(transpositions))
    untransposed = [untranspose(r, transpositions) for r in rows]
    if fillcolumnwise:
        return combine_every_nth(untransposed)
    else:
        return cat(chain(*untransposed))

def scytale_encipher(message, rows, fillvalue=' '):
    """Enciphers using the scytale transposition cipher. `rows` is the 
    circumference of the rod. The message is fitted inot columns so that
    all rows are used.
    
    Message is padded with spaces to allow all rows to be the same length.

    For ease of implementation, the cipher is performed on the transpose
    of the grid

    >>> scytale_encipher('thequickbrownfox', 3)
    'tcnhkfeboqrxuo iw '
    >>> scytale_encipher('thequickbrownfox', 4)
    'tubnhirfecooqkwx'
    >>> scytale_encipher('thequickbrownfox', 5)
    'tubn hirf ecoo qkwx '
    >>> scytale_encipher('thequickbrownfox', 6)
    'tqcrnxhukof eibwo '
    >>> scytale_encipher('thequickbrownfox', 7)
    'tqcrnx hukof  eibwo  '
    """
    # transpositions = [i for i in range(math.ceil(len(message) / rows))]
    # return column_transposition_encipher(message, transpositions, 
    #     fillvalue=fillvalue, fillcolumnwise=False, emptycolumnwise=True)
    transpositions = (i for i in range(rows))
    return column_transposition_encipher(message, transpositions, 
        fillvalue=fillvalue, fillcolumnwise=True, emptycolumnwise=False)

def scytale_decipher(message, rows):
    """Deciphers using the scytale transposition cipher.
    Assumes the message is padded so that all rows are the same length.
    
    >>> scytale_decipher('tcnhkfeboqrxuo iw ', 3)
    'thequickbrownfox  '
    >>> scytale_decipher('tubnhirfecooqkwx', 4)
    'thequickbrownfox'
    >>> scytale_decipher('tubn hirf ecoo qkwx ', 5)
    'thequickbrownfox    '
    >>> scytale_decipher('tqcrnxhukof eibwo ', 6)
    'thequickbrownfox  '
    >>> scytale_decipher('tqcrnx hukof  eibwo  ', 7)
    'thequickbrownfox     '
    """
    # transpositions = [i for i in range(math.ceil(len(message) / rows))]
    # return column_transposition_decipher(message, transpositions, 
    #     fillcolumnwise=False, emptycolumnwise=True)
    transpositions = [i for i in range(rows)]
    return column_transposition_decipher(message, transpositions, 
        fillcolumnwise=True, emptycolumnwise=False)


def column_transposition_break(message, translist=None,
                                  fitness=Pbigrams, chunksize=500):
    """Breaks a column transposition cipher using a dictionary and
    n-gram frequency analysis

    If `translist` is not specified, use 
    [`szyfrow.support.langauge_models.transpositions`](support/language_models.html#szyfrow.support.language_models.transpositions).

    >>> len(keywords)
    20

    >>> column_transposition_break(column_transposition_encipher(sanitise( \
            "It is a truth universally acknowledged, that a single man in \
             possession of a good fortune, must be in want of a wife. However \
             little known the feelings or views of such a man may be on his \
             first entering a neighbourhood, this truth is so well fixed in \
             the minds of the surrounding families, that he is considered the \
             rightful property of some one or other of their daughters."), \
        'encipher'), \
        translist={(2, 0, 5, 3, 1, 4, 6): ['encipher'], \
                   (5, 0, 6, 1, 3, 4, 2): ['fourteen'], \
                   (6, 1, 0, 4, 5, 3, 2): ['keyword']}) # doctest: +ELLIPSIS
    (((2, 0, 5, 3, 1, 4, 6), False, False), -709.4646722...)
    >>> column_transposition_break(column_transposition_encipher(sanitise( \
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
        fitness=Ptrigrams) # doctest: +ELLIPSIS
    (((2, 0, 5, 3, 1, 4, 6), False, False), -997.0129085...)
    """
    if translist is None:
        translist = transpositions

    with multiprocessing.Pool() as pool:
        helper_args = [(message, trans, fillcolumnwise, emptycolumnwise,
                        fitness)
                       for trans in translist
                       for fillcolumnwise in [True, False]
                       for emptycolumnwise in [True, False]]
        # Gotcha: the helper function here needs to be defined at the top level
        #   (limitation of Pool.starmap)
        breaks = pool.starmap(column_transposition_break_worker,
                              helper_args, chunksize) 
        return max(breaks, key=lambda k: k[1])

def column_transposition_break_worker(message, transposition,
        fillcolumnwise, emptycolumnwise, fitness):
    plaintext = column_transposition_decipher(message, transposition,
        fillcolumnwise=fillcolumnwise, emptycolumnwise=emptycolumnwise)
    fit = fitness(sanitise(plaintext))
    return (transposition, fillcolumnwise, emptycolumnwise), fit


def scytale_break(message, max_key_length=20,
                     fitness=Pbigrams, chunksize=500):
    """Breaks a scytale cipher using a range of lengths and
    n-gram frequency analysis

    >>> scytale_break(scytale_encipher(sanitise( \
            "It is a truth universally acknowledged, that a single man in \
             possession of a good fortune, must be in want of a wife. However \
             little known the feelings or views of such a man may be on his \
             first entering a neighbourhood, this truth is so well fixed in \
             the minds of the surrounding families, that he is considered the \
             rightful property of some one or other of their daughters."), \
        5)) # doctest: +ELLIPSIS
    (5, -709.4646722...)
    >>> scytale_break(scytale_encipher(sanitise( \
            "It is a truth universally acknowledged, that a single man in \
             possession of a good fortune, must be in want of a wife. However \
             little known the feelings or views of such a man may be on his \
             first entering a neighbourhood, this truth is so well fixed in \
             the minds of the surrounding families, that he is considered the \
             rightful property of some one or other of their daughters."), \
        5), \
        fitness=Ptrigrams) # doctest: +ELLIPSIS
    (5, -997.0129085...)
    """
    with multiprocessing.Pool() as pool:
        helper_args = [(message, trans, False, True, fitness)
            for trans in
                [[col for col in range(math.ceil(len(message)/rows))]
                    for rows in range(1,max_key_length+1)]]
        # Gotcha: the helper function here needs to be defined at the top level
        #   (limitation of Pool.starmap)
        breaks = pool.starmap(column_transposition_break_worker,
                              helper_args, chunksize)
        best = max(breaks, key=lambda k: k[1])
        return math.trunc(len(message) / len(best[0][0])), best[1]

if __name__ == "__main__":
    import doctest