import pytest
import string 

from szyfrow.amsco import *
from szyfrow.support.utilities import *
from szyfrow.support.language_models import transpositions_of

def test_positions():
    grid = amsco_positions(string.ascii_lowercase, 'freddy', fillpattern=(1, 2))
    assert grid == [[AmscoSlice(index=3, start=4, end=6),
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

def test_encipher_message():
    ciphertext = amsco_encipher('hellothere', 'abc', fillpattern=(1, 2))
    assert ciphertext == 'hoteelhler'

    ciphertext = amsco_encipher('hellothere', 'abc', fillpattern=(2, 1))
    assert ciphertext == 'hetelhelor'

    ciphertext = amsco_encipher('hellothere', 'acb', fillpattern=(1, 2))
    assert ciphertext == 'hotelerelh'

    ciphertext = amsco_encipher('hellothere', 'acb', fillpattern=(2, 1))
    assert ciphertext == 'hetelorlhe'

    ciphertext = amsco_encipher('hereissometexttoencipher', 'encode')
    assert ciphertext == 'etecstthhomoerereenisxip'

    ciphertext = amsco_encipher('hereissometexttoencipher', 'cipher', fillpattern=(1, 2))
    assert ciphertext == 'hetcsoeisterereipexthomn'

    ciphertext = amsco_encipher('hereissometexttoencipher', 'cipher', fillpattern=(1, 2), fillstyle=AmscoFillStyle.continuous)
    assert ciphertext == 'hecsoisttererteipexhomen'

    ciphertext = amsco_encipher('hereissometexttoencipher', 'cipher', fillpattern=(2, 1))
    assert ciphertext == 'heecisoosttrrtepeixhemen'

    ciphertext = amsco_encipher('hereissometexttoencipher', 'cipher', fillpattern=(1, 3, 2))
    assert ciphertext == 'hxtomephescieretoeisnter'

    ciphertext = amsco_encipher('hereissometexttoencipher', 'cipher', fillpattern=(1, 3, 2), fillstyle=AmscoFillStyle.continuous)
    assert ciphertext == 'hxomeiphscerettoisenteer'


def test_decipher_message():
    plaintext = 'hereissometexttoencipher'
    for key in ['bayes', 'samplekey']:
        for fillpattern in [(1, 2), (2, 1)]:
            for fillstyle in AmscoFillStyle:
                enciphered = amsco_encipher(plaintext, key, 
                    fillpattern=fillpattern, fillstyle=fillstyle)
                deciphered = amsco_decipher(enciphered, key, 
                    fillpattern=fillpattern, fillstyle=fillstyle)
                assert deciphered == plaintext


def test_amsco_break():
    plaintext = sanitise('''It is a truth universally acknowledged, that a single man in
             possession of a good fortune, must be in want of a wife. However
             little known the feelings or views of such a man may be on his 
             first entering a neighbourhood, this truth is so well fixed in
             the minds of the surrounding families, that he is considered the
             rightful property of some one or other of their daughters.''')
    expected_key = 'encipher'
    expected_fillpattern = (1, 2)
    expected_fillsytle = AmscoFillStyle.continuous
    expected_score = Pbigrams(plaintext)
    ciphertext = amsco_encipher(plaintext, expected_key, 
        fillpattern=expected_fillpattern, fillstyle=expected_fillsytle)
    used_translist = collections.defaultdict(list)
    for word in 'encipher fourteen keyword'.split():
        used_translist[transpositions_of(word)] += [word]

    (key, fillpattern, fillstyle), score = amsco_break(ciphertext, 
        translist=used_translist)

    assert key == transpositions_of(expected_key)
    assert fillpattern == expected_fillpattern
    assert fillstyle == expected_fillsytle
    assert score == pytest.approx(expected_score)
