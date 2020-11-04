"""Enciphering and deciphering using the [Cadenus cipher](https://www.thonky.com/kryptos/cadenus-cipher). 
Also attempts to break messages that use a Cadenus cipher.

The plaintext is written out in a grid, with one column per letter of the 
keyword. The plaintext is written out left to right in rows. The plaintext 
needs to fill 25 rows: if it is shorter, the text is padded; if longer, it is
broken into 25-row chunks.

For instance, the 100 letter chunk:

> Whoever has made a voyage up the Hudson must remember the Kaatskill mountains. 
> They are a dismembered branch of the great

and the keyword "wink" would written out as the leftmost grid below.

The columns are then rotated according to the _keycolumn_. For each column, the
keyword letter in that column is found in the keycolumn. This identifies a 
specific row in the grid. That column only is rotated upwards until the selected
row is at the top of the column. Each column is rotated independently, according
to its keyword letter.

For instance, the middle grid below is formed from the leftmost grid by 
rotating the first column up four positions, the second column up 17 positions,
and so on. (The letters chosen to head the new colums are capitalised in the
leftmost grid.)

Finally, each row is transposed given the alphabetic order of the keyword (as
seen in the rightmost grid below).

The ciphertext is read out in rows, starting with the now-leftmost column. For
the example, the ciphertext would be 

> antodeleeeuhrsidrbhmhdrrhnimefmthgeaetakseomehetyaasuvoyegrastmmuuaeenabbtpchehtarorikswosmvaleatned'

```
w i n k         w i n k    i k n w
-------         -------    -------
w h o e    a    o a t n    a n t o
v e r h    z    e d l e    d e l e
a s m a    y    h e u e    e e u h
d e a v    x    d r i s    r s i d
O y a g    vw   m r h b    r b h m
e u p t    u    r h r d    h d r r
h e h u    t    m h i n    h n i m
d s o n    s    t e m f    e f m t
m u s t    r    a h e g    h g e a
r e m e    q    k e a t    e t a k
m b e r    p    m s o e    s e o m
t h e k    o    t e e h    e h e t
a a T s    n    s y a a    y a a s
k i l l    m    y u o v    u v o y
m o u n    l    a e r g    e g r a
t a i N    k    m s m t    s t m m
s t h e    j    e u a u    u u a e
y A r e    i    b e a n    e n a b
a d i s    h    c b p t    b t p c
m e m b    g    t h h e    h e h t
e r e d    f    r a o r    a r o r
b r a n    e    w i s k    i k s w
c h o f    d    v o m s    o s m v
t h e g    c    a a e l    a l e a
r e a t    b    d t e n    t n e d
```

"""
from itertools import chain
import multiprocessing
from szyfrow.support.utilities import *
from szyfrow.support.language_models import *


def make_cadenus_keycolumn(doubled_letters = 'vw', start='a', reverse=False):
    """Makes the key column for a Cadenus cipher (the column down between the
        rows of letters)

    >>> make_cadenus_keycolumn()['a']
    0
    >>> make_cadenus_keycolumn()['b']
    1
    >>> make_cadenus_keycolumn()['c']
    2
    >>> make_cadenus_keycolumn()['v']
    21
    >>> make_cadenus_keycolumn()['w']
    21
    >>> make_cadenus_keycolumn()['z']
    24
    >>> make_cadenus_keycolumn(doubled_letters='ij', start='b', reverse=True)['a']
    1
    >>> make_cadenus_keycolumn(doubled_letters='ij', start='b', reverse=True)['b']
    0
    >>> make_cadenus_keycolumn(doubled_letters='ij', start='b', reverse=True)['c']
    24
    >>> make_cadenus_keycolumn(doubled_letters='ij', start='b', reverse=True)['i']
    18
    >>> make_cadenus_keycolumn(doubled_letters='ij', start='b', reverse=True)['j']
    18
    >>> make_cadenus_keycolumn(doubled_letters='ij', start='b', reverse=True)['v']
    6
    >>> make_cadenus_keycolumn(doubled_letters='ij', start='b', reverse=True)['z']
    2
    """
    index_to_remove = string.ascii_lowercase.find(doubled_letters[0])
    short_alphabet = string.ascii_lowercase[:index_to_remove] + string.ascii_lowercase[index_to_remove+1:]
    if reverse:
        short_alphabet = cat(reversed(short_alphabet))
    start_pos = short_alphabet.find(start)
    rotated_alphabet = short_alphabet[start_pos:] + short_alphabet[:start_pos]
    keycolumn = {l: i for i, l in enumerate(rotated_alphabet)}
    keycolumn[doubled_letters[0]] = keycolumn[doubled_letters[1]]
    return keycolumn

def cadenus_encipher(message, keyword, keycolumn, fillvalue='a'):
    """Encipher with the Cadenus cipher

    >>> cadenus_encipher(sanitise('Whoever has made a voyage up the Hudson ' \
                                  'must remember the Kaatskill mountains. ' \
                                  'They are a dismembered branch of the great'), \
                'wink', \
                make_cadenus_keycolumn(doubled_letters='vw', start='a', reverse=True))
    'antodeleeeuhrsidrbhmhdrrhnimefmthgeaetakseomehetyaasuvoyegrastmmuuaeenabbtpchehtarorikswosmvaleatned'
    >>> cadenus_encipher(sanitise('a severe limitation on the usefulness of ' \
                                  'the cadenus is that every message must be ' \
                                  'a multiple of twenty-five letters long'), \
                'easy', \
                make_cadenus_keycolumn(doubled_letters='vw', start='a', reverse=True))
    'systretomtattlusoatleeesfiyheasdfnmschbhneuvsnpmtofarenuseieeieltarlmentieetogevesitfaisltngeeuvowul'
    """
    transpositions = transpositions_of(keyword)
    enciphered_chunks = []
    for message_chunk in chunks(message, len(transpositions) * 25, 
                                fillvalue=fillvalue):
        rows = chunks(message_chunk, len(transpositions), fillvalue=fillvalue)
        columns = zip(*rows)
        rotated_columns = [col[start:] + col[:start] for start, col in zip([keycolumn[l] for l in keyword], columns)]    
        rotated_rows = zip(*rotated_columns)
        transposed = [transpose(r, transpositions) for r in rotated_rows]
        enciphered_chunks.append(cat(chain(*transposed)))
    return cat(enciphered_chunks)

def cadenus_decipher(message, keyword, keycolumn, fillvalue='a'):
    """
    >>> cadenus_decipher('antodeleeeuhrsidrbhmhdrrhnimefmthgeaetakseomehetyaa' \
                         'suvoyegrastmmuuaeenabbtpchehtarorikswosmvaleatned', \
                 'wink', \
                 make_cadenus_keycolumn(reverse=True))
    'whoeverhasmadeavoyageupthehudsonmustrememberthekaatskillmountainstheyareadismemberedbranchofthegreat'
    >>> cadenus_decipher('systretomtattlusoatleeesfiyheasdfnmschbhneuvsnpmtof' \
                        'arenuseieeieltarlmentieetogevesitfaisltngeeuvowul', \
                 'easy', \
                 make_cadenus_keycolumn(reverse=True))
    'aseverelimitationontheusefulnessofthecadenusisthateverymessagemustbeamultipleoftwentyfiveletterslong'
    """
    transpositions = transpositions_of(keyword)
    deciphered_chunks = []
    for message_chunk in chunks(message, len(transpositions) * 25, 
                                fillvalue=fillvalue):
        rows = chunks(message_chunk, len(transpositions), fillvalue=fillvalue)
        untransposed_rows = [untranspose(r, transpositions) for r in rows]
        columns = zip(*untransposed_rows)
        rotated_columns = [col[-start:] + col[:-start] for start, col in zip([keycolumn[l] for l in keyword], columns)]    
        rotated_rows = zip(*rotated_columns)
        deciphered_chunks.append(cat(chain(*rotated_rows)))
    return cat(deciphered_chunks)
    


def cadenus_break(message, wordlist=None, 
    doubled_letters='vw', fitness=Pbigrams):
    """Breaks a Cadenus cipher using a dictionary and
    frequency analysis

    If `wordlist` is not specified, use 
    [`szyfrow.support.langauge_models.keywords`](support/language_models.html#szyfrow.support.language_models.keywords).
    """
    if wordlist is None:
        wordlist = keywords

    # c = make_cadenus_keycolumn(reverse=True)
    # valid_words = [w for w in wordlist
    #     if len(transpositions_of(w)) == len(message) // 25]
    with multiprocessing.Pool() as pool:
        results = pool.starmap(cadenus_break_worker, 
                [(message, w, 
                    make_cadenus_keycolumn(doubled_letters=doubled_letters, 
                        start=s, reverse=r), 
                    fitness)
                for w in wordlist 
                for s in string.ascii_lowercase 
                for r in [True, False]
                # if max(transpositions_of(w)) <= len(
                #     make_cadenus_keycolumn(
                #         doubled_letters=doubled_letters, start=s, reverse=r))
                ])
    # return list(results)
    return max(results, key=lambda k: k[1])

def cadenus_break_worker(message, keyword, keycolumn, fitness):
    # message_chunks = chunks(message, 175)
    # plaintext = ''.join(cadenus_decipher(c, keyword, keycolumn) for c in message_chunks)
    plaintext = cadenus_decipher(message, keyword, keycolumn)
    fit = fitness(plaintext)
    return (keyword, keycolumn), fit

if __name__ == "__main__":
    import doctest