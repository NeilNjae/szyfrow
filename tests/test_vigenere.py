import pytest
import string 

from szyfrow.vigenere import *
from szyfrow.support.utilities import *


def test_vigenere_encipher_message():
    enciphered = vigenere_encipher('hello', 'abc')
    expected = 'hfnlp'
    assert enciphered == expected


def test_vigenere_decipher_message():
    deciphered = vigenere_decipher('hfnlp', 'abc')
    expected = 'hello'
    assert deciphered == expected

def test_beaufort_encipher_message():
    enciphered = beaufort_encipher('inhisjournaldatedtheidesofoctober', 'arcanaimperii')
    expected = 'sevsvrusyrrxfayyxuteemazudmpjmmwr'
    assert enciphered == expected

def test_beaufort_decipher_message():
    deciphered = beaufort_encipher('sevsvrusyrrxfayyxuteemazudmpjmmwr', 'arcanaimperii')
    expected = 'inhisjournaldatedtheidesofoctober'
    assert deciphered == expected


def test_vigenere_keyword_break():
    ciphertext = vigenere_encipher(sanitise('this is a test message for the vigenere decipherment'), 'cat')
    expected_key = 'cat'
    expected_score = -52.9472712

    actual_key, actual_score = vigenere_keyword_break(ciphertext, wordlist=['cat', 'elephant', 'kangaroo'])
    assert expected_key == actual_key
    assert expected_score == pytest.approx(actual_score)

def test_vigenere_frequency_break():
    ciphertext = vigenere_encipher(sanitise("It is time to " \
            "run. She is ready and so am I. I stole Daniel's pocketbook this " \
            "afternoon when he left his jacket hanging on the easel in the " \
            "attic. I jump every time I hear a footstep on the stairs, " \
            "certain that the theft has been discovered and that I will " \
            "be caught. The SS officer visits less often now that he is " \
            "sure"), 'florence')
    expected_key = 'florence'
    expected_score = -307.5473096
    actual_key, actual_score = vigenere_frequency_break(ciphertext)
    assert expected_key == actual_key
    assert expected_score == pytest.approx(actual_score)


def test_beaufort_sub_break():

    ciphertext = 'samwpplggnnmmyaazgympjapopnwiywwomwspgpjmefwmawx' \
      'jafjhxwwwdigxshnlywiamhyshtasxptwueahhytjwsn'
    expected_key = 0
    expected_score = -117.4492
    actual_key, actual_score = beaufort_sub_break(ciphertext)
    assert expected_key == actual_key
    assert expected_score == pytest.approx(actual_score)

    ciphertext = 'eyprzjjzznxymrygryjqmqhznjrjjapenejznawngnnezgza' \
      'dgndknaogpdjneadadazlhkhxkryevrronrmdjnndjlo'
    expected_key = 17
    expected_score = -114.9598
    actual_key, actual_score = beaufort_sub_break(ciphertext)
    assert expected_key == actual_key
    assert expected_score == pytest.approx(actual_score)


def test_beaufort_frequency_break():
    ciphertext = beaufort_encipher(sanitise("It is time to " \
            "run. She is ready and so am I. I stole Daniel's pocketbook this " \
            "afternoon when he left his jacket hanging on the easel in the " \
            "attic. I jump every time I hear a footstep on the stairs, " \
            "certain that the theft has been discovered and that I will " \
            "be caught. The SS officer visits less often now that he is " \
            "sure"), 'florence')
    expected_key = 'florence'
    expected_score = -307.5473096
    actual_key, actual_score = beaufort_frequency_break(ciphertext)
    assert expected_key == actual_key
    assert expected_score == pytest.approx(actual_score)


def test_beaufort_variant_frequency_break():
    ciphertext = beaufort_variant_encipher(sanitise("It is time to " \
            "run. She is ready and so am I. I stole Daniel's pocketbook this " \
            "afternoon when he left his jacket hanging on the easel in the " \
            "attic. I jump every time I hear a footstep on the stairs, " \
            "certain that the theft has been discovered and that I will " \
            "be caught. The SS officer visits less often now that he is " \
            "sure"), 'florence')
    expected_key = 'florence'
    expected_score = -307.5473096
    actual_key, actual_score = beaufort_variant_frequency_break(ciphertext)
    assert expected_key == actual_key
    assert expected_score == pytest.approx(actual_score)
