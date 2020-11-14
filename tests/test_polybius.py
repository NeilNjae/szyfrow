import pytest
import string 

from szyfrow.polybius import *
from szyfrow.support.utilities import *

def test_grid():
    grid = polybius_grid('a', 'abcde', 'abcde')
    assert grid['x'] == ('e', 'c')
    grid = polybius_grid('elephant', 'abcde', 'abcde')
    assert grid['e'] == ('a', 'a')
    assert grid['b'] == ('b', 'c')

def test_reverse_grid():
    grid = polybius_reverse_grid('a', 'abcde', 'abcde')
    assert grid['e', 'c'] == 'x'
    grid = polybius_reverse_grid('elephant', 'abcde', 'abcde')
    assert grid['a', 'a'] == 'e'
    assert grid['b', 'c'] == 'b'

def test_grid_round_trip():
    ltm = {'j': 'i'}
    fgrid = polybius_grid('elephant', 'abcde', 'abcde', 
        letters_to_merge=ltm)
    rgrid = polybius_reverse_grid('elephant', 'abcde', 'abcde', 
        letters_to_merge=ltm)
    for l in fgrid:
        if l in ltm:
            assert ltm[l] == rgrid[fgrid[l]]
        else:
            assert l == rgrid[fgrid[l]]
    for p in rgrid:
        assert p == fgrid[rgrid[p]]


def test_polybius_flatten():
    assert polybius_flatten(('a', 'b'), column_first=True) == 'ba'
    assert polybius_flatten(('a', 'b'), column_first=False) == 'ab'


def test_encipher_message():
    ct = polybius_encipher('this is a test message for the ' \
          'polybius decipherment', 'elephant', \
          [1, 2, 3, 4, 5], [1, 2, 3, 4, 5], \
          wrap_alphabet=KeywordWrapAlphabet.from_last)
    assert ct == '2214445544551522115522511155551543114252542214111352123234442355411135441314115451112122'
    
    ct = polybius_encipher('this is a test message for the ' \
          'polybius decipherment', 'elephant', 'abcde', 'abcde', \
          column_first=False)
    assert ct == 'bbadccddccddaebbaaddbbceaaddddaecbaacadadcbbadaaacdaabedbcccdeddbeaabdccacadaadcceaababb'
    
    ct = polybius_encipher('this is a test message for the ' \
          'polybius decipherment', 'elephant', 'abcde', 'abcde', \
          column_first=True)
    assert ct == 'bbdaccddccddeabbaaddbbecaaddddeabcaaacadcdbbdaaacaadbadecbccedddebaadbcccadaaacdecaaabbb'


def test_decipher_message():
    plaintext = sanitise('''Whoever has made a voyage up the Hudson must 
        remember the Kaatskill mountains. They are a dismembered branch of 
        the great''')
    for key in ['wink', 'elephant', 'swashbuckling']: 
        enciphered = polybius_encipher(plaintext, key, 'abcde', 'abcde')
        deciphered = polybius_decipher(enciphered, key, 'abcde', 'abcde')
        assert deciphered == plaintext


def test_cadenus_break():
    plaintext = sanitise('''You will rejoice to hear that no disaster has accompanied the
        commencement of an enterprise which you have regarded with such evil
        forebodings.  I arrived here yesterday, and my first task is to assure
        my dear sister of my welfare and increasing confidence in the success
        of my undertaking.''')
    expected_key = 'swashbuckling'
    expected_wrap = KeywordWrapAlphabet.from_last
    expected_row_order = 'abcde'
    expected_col_order = 'abcde'
    expected_col_first = True
    ciphertext = polybius_encipher(plaintext, expected_key, 
        expected_col_order, expected_row_order, 
        column_first=expected_col_first, wrap_alphabet=expected_wrap)
    
    trans_table = ''.maketrans('j', 'i')
    expected_score = Ptrigrams(plaintext.translate(trans_table))

    dictionary = ['clearinghouse', 'computerising', 'counterclaims', 
        'housewarmings',  'intravenously', 'liquefactions', 'somersaulting', 
        'sportsmanlike', 'swashbuckling']

    # dictionary = ['swashbuckling']

    (key, wrap, col_order, row_order, col_first), score = polybius_break(ciphertext, 
        expected_col_order, expected_row_order, 
        wordlist=dictionary, fitness=Ptrigrams)

    assert key == expected_key
    assert wrap == expected_wrap
    assert col_first == expected_col_first
    assert score == pytest.approx(expected_score)
