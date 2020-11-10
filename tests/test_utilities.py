import pytest
import string 

from szyfrow.support.utilities import *

def test_pos():
	for n, l in enumerate(string.ascii_lowercase):
		assert n == pos(l)
	for n, l in enumerate(string.ascii_uppercase):
		assert n == pos(l)
	with pytest.raises(ValueError):
		pos('9')

def test_unpos():
	for n, l in enumerate(string.ascii_lowercase):
		assert l == unpos(n)
		assert l == unpos(n + 26)
	for n, l in enumerate(string.ascii_uppercase):
		assert l.lower() == unpos(n)
	with pytest.raises(ValueError):
		pos('9')

def test_pad():
    assert pad(10, 3, '*') == '**'
    assert pad(10, 5, '*') == ''
    assert pad(10, 3, lambda: '!') == '!!'

def test_every_nth():
	assert every_nth(string.ascii_lowercase, 5) == ['afkpuz', 'bglqv', 'chmrw', 'dinsx', 'ejoty']
	assert every_nth(string.ascii_lowercase, 1) == ['abcdefghijklmnopqrstuvwxyz']
	assert every_nth(string.ascii_lowercase, 26) == ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
	assert every_nth(string.ascii_lowercase, 5, fillvalue='!') == ['afkpuz', 'bglqv!', 'chmrw!', 'dinsx!', 'ejoty!']

def test_combine_every_nth():
    for i in range(1, 27):
        assert combine_every_nth(every_nth(string.ascii_lowercase, 5)) == string.ascii_lowercase


def test_chunks_on_text():
    assert chunks('abcdefghi', 3) == ['abc', 'def', 'ghi']
    assert chunks('abcdefghi', 4) == ['abcd', 'efgh', 'i']
    assert chunks('abcdefghi', 4, fillvalue='!') == ['abcd', 'efgh', 'i!!!']

def test_chunks_on_nontext():
    ns = [1,2,3,4,5,6,7,8,9]
    assert chunks(ns, 3) == [[1,2,3],[4,5,6],[7,8,9]]

def test_transpose():
    assert transpose(['a', 'b', 'c', 'd'], (0,1,2,3)) == ['a', 'b', 'c', 'd']
    assert transpose(['a', 'b', 'c', 'd'], (3,1,2,0)) == ['d', 'b', 'c', 'a']
    assert transpose([10,11,12,13,14,15], (3,2,4,1,5,0)) == [13, 12, 14, 11, 15, 10]

def test_untranspose():
    assert untranspose(['a', 'b', 'c', 'd'], [0,1,2,3]) == ['a', 'b', 'c', 'd']
    assert untranspose(['d', 'b', 'c', 'a'], [3,1,2,0]) == ['a', 'b', 'c', 'd']
    assert untranspose([13, 12, 14, 11, 15, 10], [3,2,4,1,5,0]) == [10, 11, 12, 13, 14, 15]

def test_letters():
    assert letters('The Quick') == 'TheQuick'
    assert letters('The Quick BROWN fox jumped! over... the (9lazy) DOG') == 'TheQuickBROWNfoxjumpedoverthelazyDOG'

def test_unaccent():
    assert unaccent('hello') == 'hello'
    assert unaccent('HELLO') == 'HELLO'
    assert unaccent('héllo') == 'hello'
    assert unaccent('héllö') == 'hello'
    assert unaccent('HÉLLÖ') == 'HELLO'

def test_sanitise():
    assert sanitise('The Quick') == 'thequick'
    assert sanitise('The Quick BROWN fox jumped! over... the (9lazy) DOG') == 'thequickbrownfoxjumpedoverthelazydog'
    assert sanitise('HÉLLÖ') == 'hello'

    