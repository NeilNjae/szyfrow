import pytest
import string 

from szyfrow.column_transposition import *
from szyfrow.support.utilities import *

def test_encipher_message():
    ciphertext =  column_transposition_encipher('hellothere', 'abcdef', fillcolumnwise=True)
    assert ciphertext == 'hlohr eltee '
    ciphertext =  column_transposition_encipher('hellothere', 'abcdef', fillcolumnwise=True, emptycolumnwise=True)
    assert ciphertext == 'hellothere  '
    ciphertext =  column_transposition_encipher('hellothere', 'abcdef')
    assert ciphertext == 'hellothere  '
    ciphertext =  column_transposition_encipher('hellothere', 'abcde')
    assert ciphertext == 'hellothere'
    ciphertext =  column_transposition_encipher('hellothere', 'abcde', fillcolumnwise=True, emptycolumnwise=True)
    assert ciphertext == 'hellothere'
    ciphertext =  column_transposition_encipher('hellothere', 'abcde', fillcolumnwise=True, emptycolumnwise=False)
    assert ciphertext == 'hlohreltee'
    ciphertext =  column_transposition_encipher('hellothere', 'abcde', fillcolumnwise=False, emptycolumnwise=True)
    assert ciphertext == 'htehlelroe'
    ciphertext =  column_transposition_encipher('hellothere', 'abcde', fillcolumnwise=False, emptycolumnwise=False)
    assert ciphertext == 'hellothere'
    ciphertext =  column_transposition_encipher('hellothere', 'clever', fillcolumnwise=True, emptycolumnwise=True)
    assert ciphertext == 'heotllrehe'
    ciphertext =  column_transposition_encipher('hellothere', 'clever', fillcolumnwise=True, emptycolumnwise=False)
    assert ciphertext == 'holrhetlee'
    ciphertext =  column_transposition_encipher('hellothere', 'clever', fillcolumnwise=False, emptycolumnwise=True)
    assert ciphertext == 'htleehoelr'
    ciphertext =  column_transposition_encipher('hellothere', 'clever', fillcolumnwise=False, emptycolumnwise=False)
    assert ciphertext == 'hleolteher'
    ciphertext =  column_transposition_encipher('hellothere', 'cleverly')
    assert ciphertext == 'hleolthre e '
    ciphertext =  column_transposition_encipher('hellothere', 'cleverly', fillvalue='!')
    assert ciphertext == 'hleolthre!e!'
    ciphertext =  column_transposition_encipher('hellothere', 'cleverly', fillvalue=lambda: '*')
    assert ciphertext == 'hleolthre*e*'

def test_decipher_message():
    plaintext = 'hereissometexttoencipher'
    for key in ['bayes', 'samplekey']:
        for fillcolumnwise in [True, False]:
            for emptycolumnwise in [True, False]:
                enciphered = column_transposition_encipher(plaintext, key, 
                    fillcolumnwise=fillcolumnwise, emptycolumnwise=emptycolumnwise)
                deciphered = column_transposition_decipher(enciphered, key, 
                    fillcolumnwise=fillcolumnwise, emptycolumnwise=emptycolumnwise)
                assert deciphered.strip() == plaintext


def test_encipher_scytale():
    assert scytale_encipher('thequickbrownfox', 3) == 'tcnhkfeboqrxuo iw '
    assert scytale_encipher('thequickbrownfox', 4) == 'tubnhirfecooqkwx'
    assert scytale_encipher('thequickbrownfox', 5) == 'tubn hirf ecoo qkwx '
    assert scytale_encipher('thequickbrownfox', 6) == 'tqcrnxhukof eibwo '
    assert scytale_encipher('thequickbrownfox', 7) == 'tqcrnx hukof  eibwo  '

def test_decipher_scytale():
    plaintext = 'hereissometexttoencipher'
    for key in range(3, 8):
        enciphered = scytale_encipher(plaintext, key)
        deciphered = scytale_decipher(enciphered, key)
        assert deciphered.strip() == plaintext

def test_column_transposition_break():
    plaintext = sanitise('''It is a truth universally acknowledged, that a single man in
             possession of a good fortune, must be in want of a wife. However
             little known the feelings or views of such a man may be on his 
             first entering a neighbourhood, this truth is so well fixed in
             the minds of the surrounding families, that he is considered the
             rightful property of some one or other of their daughters.''')
    expected_key = 'encipher'
    expected_fill = False
    expected_empty = True
    expected_score = Pbigrams(plaintext)
    ciphertext = column_transposition_encipher(plaintext, expected_key, 
        fillcolumnwise=expected_fill, emptycolumnwise=expected_empty)
    used_translist = collections.defaultdict(list)
    for word in 'encipher fourteen keyword'.split():
        used_translist[transpositions_of(word)] += [word]

    (key, fill, empty), score = column_transposition_break(ciphertext, 
        translist=used_translist)

    assert key == transpositions_of(expected_key)
    assert fill == expected_fill
    assert empty == expected_empty
    assert score == pytest.approx(expected_score)

def test_scytale_break():
    plaintext = sanitise('''It is a truth universally acknowledged, that a single man in
             possession of a good fortune, must be in want of a wife. However
             little known the feelings or views of such a man may be on his 
             first entering a neighbourhood, this truth is so well fixed in
             the minds of the surrounding families, that he is considered the
             rightful property of some one or other of their daughters.''')
    expected_key = 5
    expected_score = Pbigrams(plaintext)
    ciphertext = scytale_encipher(plaintext, expected_key)

    key, score = scytale_break(ciphertext)

    assert key == expected_key
    assert score == pytest.approx(expected_score)
    