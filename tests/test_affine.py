import pytest
import string 

from szyfrow.affine import *
from szyfrow.support.utilities import *


def test_encipher_letter():
    for p, c in zip(
            string.ascii_letters, 
            'hknqtwzcfiloruxadgjmpsvybeHKNQTWZCFILORUXADGJMPSVYBE'):
        assert affine_encipher_letter(p, 3, 5, True) == c

    for p, c in zip(
            string.ascii_letters, 
            'filoruxadgjmpsvybehknqtwzcFILORUXADGJMPSVYBEHKNQTWZC'):
        assert affine_encipher_letter(p, 3, 5, False) == c


def test_decipher_letter():
    for p, c in zip(
            string.ascii_letters, 
            'hknqtwzcfiloruxadgjmpsvybeHKNQTWZCFILORUXADGJMPSVYBE'):
        assert affine_decipher_letter(c, 3, 5, True) == p

    for p, c in zip(
            string.ascii_letters, 
            'filoruxadgjmpsvybehknqtwzcFILORUXADGJMPSVYBEHKNQTWZC'):
        assert affine_decipher_letter(c, 3, 5, False) == p

def test_encipher_message():
    enciphered = affine_encipher(
            'hours passed during which jerico tried every trick he could think of', 
            15, 22, True)
    expected = 'lmyfu bkuusd dyfaxw claol psfaom jfasd snsfg jfaoe ls omytd jlaxe mh'
    assert enciphered == expected


def test_decipher_message():

    deciphered = affine_decipher('lmyfu bkuusd dyfaxw claol psfaom jfasd snsfg jfaoe ls omytd jlaxe mh', 
                15, 22, True)
    expected = 'hours passed during which jerico tried every trick he could think of'
    assert deciphered == expected


def test_break():
    ciphertext = '''lmyfu bkuusd dyfaxw claol psfaom jfasd snsfg jfaoe ls 
      omytd jlaxe mh jm bfmibj umis hfsul axubafkjamx. ls kffkxwsd jls 
      ofgbjmwfkiu olfmxmtmwaokttg jlsx ls kffkxwsd jlsi zg tsxwjl. jlsx 
      ls umfjsd jlsi zg hfsqysxog. ls dmmdtsd mx jls bats mh bkbsf. ls 
      bfmctsd kfmyxd jls lyj, mztanamyu xmc jm clm cku tmmeaxw kj lai 
      kxd clm ckuxj.'''
    expected_key = (15, 22, True)
    expected_score = -340.6011819
    actual_key, actual_score = affine_break(ciphertext)
    assert expected_key == actual_key
    assert expected_score == pytest.approx(actual_score)
