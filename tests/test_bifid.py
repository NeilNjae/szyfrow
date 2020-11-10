import pytest
import string 

from szyfrow.bifid import *
from szyfrow.support.utilities import *

def test_grid():
    trans, f_grid, r_grid = bifid_grid('bayes', KeywordWrapAlphabet.from_a, None)
    assert len(f_grid) == 25
    assert len(r_grid) == 25
    for l in f_grid:
        assert l == r_grid[f_grid[l]]
    assert r_grid[1, 1] == 'b'
    assert r_grid[2, 1] == 'c'


def test_encipher_message():
    assert bifid_encipher("indiajelly", 'iguana') == 'ibidonhprm'
    assert bifid_encipher("indiacurry", 'iguana', period=4, fillvalue='x') == 'ibnhgaqltzml'
    with pytest.raises(ValueError):
        bifid_encipher("indiacurry", 'iguana', period=4)


def test_decipher_message():
    plaintext = 'hereissometexttoencipher'
    for key in ['bayes', 'samplekey']:
        enciphered = bifid_encipher(plaintext, key)
        deciphered = bifid_decipher(enciphered, key)
        assert deciphered == plaintext

    for key in ['bayes', 'samplekey']:
        enciphered = bifid_encipher(plaintext, key, period=5, fillvalue='a')
        deciphered = bifid_decipher(enciphered, key, period=5, fillvalue='a')
        assert deciphered == plaintext + pad(len(plaintext), 5, 'a') 


def test_bifid_break():
    plaintext = sanitise('''It is a truth universally acknowledged, that a single man in
             possession of a good fortune, must be in want of a wife. However
             little known the feelings or views of such a man may be on his 
             first entering a neighbourhood, this truth is so well fixed in
             the minds of the surrounding families, that he is considered the
             rightful property of some one or other of their daughters.''')
    expected_key = 'encipher'
    expected_wrap = KeywordWrapAlphabet.from_a
    expected_period = 0
    expected_score = Pletters(plaintext)
    ciphertext = bifid_encipher(plaintext, expected_key, 
        wrap_alphabet=expected_wrap)
    
    (key, wrap, period), score = bifid_break(ciphertext, 
        wordlist='encipher fourteen keyword'.split())

    assert key == expected_key
    assert wrap == expected_wrap
    assert period == expected_period
    assert score == pytest.approx(expected_score)
