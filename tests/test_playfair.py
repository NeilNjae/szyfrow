import pytest
import string 

from szyfrow.playfair import *
from szyfrow.support.utilities import *

def test_wrap():
    assert playfair_wrap(3, 0, 4) == 3
    assert playfair_wrap(0, 0, 4) == 0
    assert playfair_wrap(4, 0, 4) == 4
    assert playfair_wrap(7, 0, 4) == 2
    assert playfair_wrap(-1, 0, 4) == 4

def test_encipher_bigram():
    grid = polybius_grid('playfairexample', list(range(5)), list(range(5)))

    plain_pairs = 'hi de th eg ol di nt he tr ex es tu mp'.split()
    cipher_pairs = 'bm od zb xd na be ku dm ui xm mo uv if'.split()

    for p, c in zip(plain_pairs, cipher_pairs):
        assert playfair_encipher_bigram(p, grid) == c

def test_decipher_bigram():
    grid = polybius_grid('playfairexample', list(range(5)), list(range(5)))

    plain_pairs = 'hi de th eg ol di nt he tr ex es tu mp'.split()
    cipher_pairs = 'bm od zb xd na be ku dm ui xm mo uv if'.split()

    for p, c in zip(plain_pairs, cipher_pairs):
        assert playfair_decipher_bigram(c, grid) == p

def test_playfair_bigrams():
    txt = sanitise('hide the gold in the tree stumps')
    f_bigrams = 'hi de th eg ol di nt he tr ex es tu mp sx'.split()
    t_bigrams = 'hi de th eg ol di nt he tr ex st um ps'.split()
    assert playfair_bigrams(txt, padding_replaces_repeat=True) == t_bigrams
    assert playfair_bigrams(txt, padding_replaces_repeat=False) == f_bigrams



def test_encipher_message():
    ct = playfair_encipher('hide the gold in the tree stump', 
        'playfairexample', wrap_alphabet=KeywordWrapAlphabet.from_a)
    assert ct == 'bmodzbxdnabekudmuixmmouvif'

    ct = playfair_encipher('this is a test message for the ' \
          'playfair decipherment', 'elephant')
    assert ct == 'clkrkrldhodghouhflovqbalhphzmerxnabkhapofatb'

    ct = playfair_encipher('this is a test message for the ' \
          'playfair decipherment', 'elephant', 
          wrap_alphabet=KeywordWrapAlphabet.from_last)
    assert ct == 'vlkrkrlwamnoamawdpolovalhplcklrhmnbkhahmentu'
    
    ct = playfair_encipher('''Whoever has made a voyage up the Hudson must 
        remember the Kaatskill mountains. They are a dismembered branch of 
        the great''', 'hudson')
    assert ct == 'vuelznmscupnobnwszgpaoqmonudsohephortctnqnctmoclbwepcrkffthdembgchmoczcpnbbqhrntcntcbipcaeuhlmonkpnbqz'


def test_decipher_message():
    plaintext = sanitise('''Whoever has made a voyage up the Hudson must 
        remember the Kaatskill mountains. They are a dismembered branch of 
        the great''')

    trans_table = ''.maketrans('j', 'i')

    for key in ['wink', 'elephant', 'swashbuckling']:
        for prp in [True, False]:
            expected = cat(playfair_bigrams(plaintext.translate(trans_table), 
                padding_replaces_repeat=prp))
            for wrap in KeywordWrapAlphabet:
                enciphered = playfair_encipher(plaintext, key, 
                    padding_replaces_repeat=prp, wrap_alphabet=wrap)
                deciphered = playfair_decipher(enciphered, key, 
                    padding_replaces_repeat=prp, wrap_alphabet=wrap)
                assert deciphered == expected


def test_playfair_break():
    plaintext = sanitise('''You will rejoice to hear that no disaster has accompanied the
        commencement of an enterprise which you have regarded with such evil
        forebodings.  I arrived here yesterday, and my first task is to assure
        my dear sister of my welfare and increasing confidence in the success
        of my undertaking.''')
    expected_key = 'swashbuckling'
    expected_wrap = KeywordWrapAlphabet.from_last
    expected_letters_to_merge = {'j': 'i'}
    expected_padding_letter = 'x'
    expected_padding_replaces_repeat = False
    ciphertext = playfair_encipher(plaintext, expected_key, 
        padding_letter=expected_padding_letter,
        padding_replaces_repeat=expected_padding_replaces_repeat, 
        letters_to_merge=expected_letters_to_merge, 
        wrap_alphabet=expected_wrap)


    exptected_text = playfair_decipher(ciphertext, expected_key, 
        padding_letter=expected_padding_letter,
        padding_replaces_repeat=expected_padding_replaces_repeat, 
        letters_to_merge=expected_letters_to_merge, 
        wrap_alphabet=expected_wrap)

    expected_score = Ptrigrams(exptected_text)

    dictionary = ['clearinghouse', 'computerising', 'counterclaims', 
        'housewarmings',  'intravenously', 'liquefactions', 'somersaulting', 
        'sportsmanlike', 'swashbuckling']

    # dictionary = ['swashbuckling']

    (key, wrap, letters_to_merge, padding_letter, padding_replaces_repeat), score = playfair_break(
        ciphertext, 
        letters_to_merge=expected_letters_to_merge, 
        padding_letter=expected_padding_letter,
        wordlist=dictionary, fitness=Ptrigrams)

    assert key == expected_key
    assert wrap == expected_wrap
    assert letters_to_merge == expected_letters_to_merge
    assert padding_letter == expected_padding_letter
    assert padding_replaces_repeat == expected_padding_replaces_repeat
    assert score == pytest.approx(expected_score)
