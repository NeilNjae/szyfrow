import pytest
import string 

from szyfrow.railfence import *
from szyfrow.support.utilities import *


def test_encipher_message():
    plaintext = 'hellothereavastmeheartiesthisisalongpieceoftextfortestingrailfenceciphers'
    ciphertext = railfence_encipher(plaintext, 2, fillvalue='!')
    expected = 'hlohraateerishsslnpeefetotsigaleccpeselteevsmhatetiiaogicotxfretnrifneihr!'
    assert ciphertext == expected
    ciphertext = railfence_encipher(plaintext, 3, fillvalue='!')
    expected = 'horaersslpeeosglcpselteevsmhatetiiaogicotxfretnrifneihr!!lhateihsnefttiaece!'
    assert ciphertext == expected
    ciphertext = railfence_encipher(plaintext, 5, fillvalue='!')
    expected = 'hresleogcseeemhetaocofrnrner!!lhateihsnefttiaece!!ltvsatiigitxetifih!!oarspeslp!'
    assert ciphertext == expected
    ciphertext = railfence_encipher(plaintext, 10, fillvalue='!')
    expected = 'hepisehagitnr!!lernesge!!lmtocerh!!otiletap!!tseaorii!!hassfolc!!evtitffe!!rahsetec!!eixn!'
    assert ciphertext == expected
    ciphertext = railfence_encipher(plaintext, 3)
    expected = 'horaersslpeeosglcpselteevsmhatetiiaogicotxfretnrifneihrlhateihsnefttiaece'
    assert ciphertext == expected
    ciphertext = railfence_encipher(plaintext, 5)
    expected = 'hresleogcseeemhetaocofrnrnerlhateihsnefttiaeceltvsatiigitxetifihoarspeslp'
    assert ciphertext == expected
    ciphertext = railfence_encipher(plaintext, 7)
    expected = 'haspolsevsetgifrifrlatihnettaeelemtiocxernhorersleesgcptehaiaottneihesfic'
    assert ciphertext == expected


def test_decipher_message():
    plaintext = 'hellothereavastmeheartiesthisisalongpieceoftextfortestingrailfenceciphers'
    for key in range(2, 11):
        enciphered = railfence_encipher(plaintext, key)
        deciphered = railfence_decipher(enciphered, key)
        assert deciphered == plaintext


def test_railfence_break():
    plaintext = sanitise('''It is a truth universally acknowledged, that a single man in
             possession of a good fortune, must be in want of a wife. However
             little known the feelings or views of such a man may be on his 
             first entering a neighbourhood, this truth is so well fixed in
             the minds of the surrounding families, that he is considered the
             rightful property of some one or other of their daughters.''')
    expected_key = 7
    expected_score = Ptrigrams(plaintext)
    ciphertext = railfence_encipher(plaintext, expected_key)
    
    key, score = railfence_break(ciphertext, fitness=Ptrigrams)

    assert key == expected_key
    assert score == pytest.approx(expected_score)
