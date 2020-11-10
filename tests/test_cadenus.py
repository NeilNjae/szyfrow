import pytest
import string 

from szyfrow.cadenus import *
from szyfrow.support.utilities import *

def test_keycolumn():
    assert make_cadenus_keycolumn()['a'] == 0
    assert make_cadenus_keycolumn()['b'] == 1
    assert make_cadenus_keycolumn()['c'] == 2
    assert make_cadenus_keycolumn()['v'] == 21
    assert make_cadenus_keycolumn()['w'] == 21
    assert make_cadenus_keycolumn()['z'] == 24
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['a'] == 1
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['b'] == 0
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['c'] == 24
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['i'] == 18
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['j'] == 18
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['v'] == 6
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['z'] == 2


def test_encipher_message():
    plaintext = sanitise('''Whoever has made a voyage up the Hudson must 
        remember the Kaatskill mountains. They are a dismembered branch of 
        the great''')
    keycol = make_cadenus_keycolumn(doubled_letters='vw', start='a', reverse=True)
    ciphertext = cadenus_encipher(plaintext, 'wink', keycol)
    expected = 'antodeleeeuhrsidrbhmhdrrhnimefmthgeaetakseomehetyaasuvoyegrastmmuuaeenabbtpchehtarorikswosmvaleatned'
    assert ciphertext == expected

    plaintext = sanitise('''a severe limitation on the usefulness of the 
        cadenus is that every message must be a multiple of twenty-five 
        letters long''')
    ciphertext = cadenus_encipher(plaintext, 'easy', keycol)
    expected = 'systretomtattlusoatleeesfiyheasdfnmschbhneuvsnpmtofarenuseieeieltarlmentieetogevesitfaisltngeeuvowul'
    assert ciphertext == expected


def test_decipher_message():
    plaintext = sanitise('''Whoever has made a voyage up the Hudson must 
        remember the Kaatskill mountains. They are a dismembered branch of 
        the great''')
    keycol = make_cadenus_keycolumn(doubled_letters='vw', start='a', reverse=True)
    for key in ['wink', 'easy']: 
        enciphered = cadenus_encipher(plaintext, key, keycol)
        deciphered = cadenus_decipher(enciphered, key, keycol)
        assert deciphered == plaintext


def test_cadenus_break():
    plaintext = sanitise('''It is a truth universally acknowledged, that a single man in
             possession of a good fortune, must be in want of a wife. However
             little known the feelings or views of such a man may be on his 
             first entering a neighbourhood, this truth is so well fixed in
             the minds of the surrounding families, that he is considered the
             rightful property of some one or other of their daughters.''')
    expected_key = 'swashbuckling'
    expected_score = Ptrigrams(plaintext)
    expected_keycol = make_cadenus_keycolumn(doubled_letters='vw', start='a', 
        reverse=True)

    ciphertext = cadenus_encipher(plaintext, expected_key, expected_keycol)
    
    # dictionary = ['clearinghouse', 'computerising', 'counterclaims', 
    #     'housewarmings',  'intravenously', 'liquefactions', 'somersaulting', 
    #     'sportsmanlike', 'swashbuckling']

    dictionary = ['swashbuckling']

    (key, keycol), score = cadenus_break(ciphertext, words=dictionary, 
        fitness=Ptrigrams)

    assert key == expected_key
    assert keycol == expected_keycol
    assert score == pytest.approx(expected_score)
