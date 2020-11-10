import pytest
import string 

from szyfrow.autokey import *
from szyfrow.support.utilities import *


def test_encipher_message():
    enciphered = autokey_encipher('meetatthefountain', 'kilt')
    expected = 'wmpmmxxaeyhbryoca'
    assert enciphered == expected

def test_decipher_message():
    deciphered = autokey_decipher('wmpmmxxaeyhbryoca', 'kilt')
    expected = 'meetatthefountain'
    assert deciphered == expected

# def test_break():
#     plaintext = '''hours passed during which jerico tried every trick he 
#         could think of to prompt some fresh inspiration. he arranged the 
#         cryptograms chronologically then he arranged them by length. then 
#         he sorted them by frequency. he doodled on the pile of paper. he 
#         prowled around the hut, oblivious now to who was looking at him 
#         and who wasnt.'''
#     # expected_key = 'samplekey'
#     expected_key = 'abc'
#     ciphertext = autokey_encipher(sanitise(plaintext), expected_key)
#     expected_score = Ptrigrams(sanitise(plaintext))
#     actual_key, actual_score = autokey_sa_break(ciphertext, 
#         min_keylength=len(expected_key), max_keylength=len(expected_key),
#         workers=10, max_iterations=1000, fitness=Ptrigrams
#         )
#     assert expected_key == actual_key
#     assert expected_score == pytest.approx(actual_score)
