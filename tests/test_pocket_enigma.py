import pytest
import string 

from szyfrow.pocket_enigma import *
from szyfrow.support.utilities import *

@pytest.fixture
def pe():
    return PocketEnigma(1, 'a')

def test_init(pe):
    assert pe.wheel_map == [25, 4, 23, 10, 1, 7, 9, 5, 12, 6, 3, 17, 8, 14, 13, 21, 19, 11, 20, 16, 18, 15, 24, 2, 22, 0]
    assert pe.position == 0

def test_wheel_map(pe):
    assert pe.make_wheel_map(pe.wheel2) == [2, 3, 0, 1, 22, 8, 15, 12, 5, 10, 9, 13, 7, 11, 16, 6, 14, 25, 20, 21, 18, 19, 4, 24, 23, 17]

def test_validate_wheel_map(pe):
    pe.validate_wheel_spec(pe.wheel2) == True

    with pytest.raises(ValueError):
        pe.validate_wheel_spec([])
    with pytest.raises(ValueError):
        pe.validate_wheel_spec([('a', 'b', 'c')]*13)
    with pytest.raises(ValueError):
        pe.validate_wheel_spec([('a', 'b')]*13)

def test_encipher_letter(pe):
    pe.set_position('f')
    assert pe.encipher_letter('k') == 'h'
    assert pe.position == 6

def test_lookup(pe):
    pe.set_position('f')
    assert cat([pe.lookup(l) for l in string.ascii_lowercase]) == 'udhbfejcpgmokrliwntsayqzvx'
    assert pe.lookup('A') == ''

def test_advance(pe):
    pe.set_position('f')
    assert pe.position == 5
    pe.advance()
    assert pe.position == 6

    pe.set_position('y')
    assert pe.position == 24
    pe.advance()
    assert pe.position == 25
    pe.advance()
    assert pe.position == 0

def test_encipher(pe):
    pe.set_position('f')
    assert pe.encipher('helloworld') == 'kjsglcjoqc'

    pe.set_position('f')
    assert pe.encipher('kjsglcjoqc') == 'helloworld'
    
    assert pe.encipher('helloworld', starting_position = 'x') == 'egrekthnnf'

def test_set_position(pe):
    assert pe.set_position('a') == 0
    assert pe.set_position('m') == 12
    assert pe.set_position('z') == 25

def test_break():
    assert pocket_enigma_break_by_crib('kzpjlzmoga', 1, 'h', 0) == ['a', 'f', 'q']
    assert pocket_enigma_break_by_crib('kzpjlzmoga', 1, 'he', 0) == ['a']
    assert pocket_enigma_break_by_crib('kzpjlzmoga', 1, 'll', 2) == ['a']
    assert pocket_enigma_break_by_crib('kzpjlzmoga', 1, 'l', 2) == ['a']
    assert pocket_enigma_break_by_crib('kzpjlzmoga', 1, 'l', 3) == ['a', 'j', 'n']
    assert pocket_enigma_break_by_crib('aaaaa', 1, 'l', 3) == []
    