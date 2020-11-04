import pytest
import string 

from szyfrow.caesar import *
from szyfrow.support.utilities import *


def test_encipher_letter():
    for p, c in zip(
            string.ascii_letters, 
            'fghijklmnopqrstuvwxyzabcdeFGHIJKLMNOPQRSTUVWXYZABCDE'):
        assert caesar_encipher_letter(p, 5) == c

    for p, c in zip(
            string.ascii_letters, 
            'defghijklmnopqrstuvwxyzabcDEFGHIJKLMNOPQRSTUVWXYZABC'):
        assert caesar_encipher_letter(p, 3) == c


def test_decipher_letter():
    for p, c in zip(
            string.ascii_letters, 
            'fghijklmnopqrstuvwxyzabcdeFGHIJKLMNOPQRSTUVWXYZABCDE'):
        assert caesar_decipher_letter(c, 5) == p

    for p, c in zip(
            string.ascii_letters, 
            'defghijklmnopqrstuvwxyzabcDEFGHIJKLMNOPQRSTUVWXYZABC'):
        assert caesar_decipher_letter(c, 3) == p

def test_encipher_message():
    enciphered = caesar_encipher(
            'hours passed during which jerico tried every trick he could think of', 
            15)
    expected = 'wdjgh ephhts sjgxcv lwxrw ytgxrd igxts tktgn igxrz wt rdjas iwxcz du'
    assert enciphered == expected


def test_decipher_message():

    deciphered = caesar_decipher('wdjgh ephhts sjgxcv lwxrw ytgxrd igxts tktgn igxrz wt rdjas iwxcz du', 
                15)
    expected = 'hours passed during which jerico tried every trick he could think of'
    assert deciphered == expected


def test_break():
    ciphertext = '''wdjgh ephhts sjgxcv lwxrw ytgxrd igxts tktgn igxrz wt 
        rdjas iwxcz du id egdbei hdbt ugthw xchexgpixdc. wt pggpcvts iwt 
        rgneidvgpbh rwgdcdadvxrpaan iwtc wt pggpcvts iwtb qn atcviw. iwtc 
        wt hdgits iwtb qn ugtfjtcrn. wt sddsats dc iwt exat du epetg. wt 
        egdlats pgdjcs iwt wji, dqaxkxdjh cdl id lwd lph addzxcv pi wxb 
        pcs lwd lphci.'''
    expected_key = 15
    expected_score = -340.6011819
    actual_key, actual_score = caesar_break(ciphertext)
    assert expected_key == actual_key
    assert expected_score == pytest.approx(actual_score)
