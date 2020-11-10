import pytest
import string 

from szyfrow.keyword_cipher import *
from szyfrow.support.utilities import *

def test_cipher_alphabet():
    assert keyword_cipher_alphabet_of('bayes') == 'bayescdfghijklmnopqrtuvwxz'
    assert keyword_cipher_alphabet_of('bayes', KeywordWrapAlphabet.from_a) == 'bayescdfghijklmnopqrtuvwxz'
    assert keyword_cipher_alphabet_of('bayes', KeywordWrapAlphabet.from_last) == 'bayestuvwxzcdfghijklmnopqr'
    assert keyword_cipher_alphabet_of('bayes', KeywordWrapAlphabet.from_largest) == 'bayeszcdfghijklmnopqrtuvwx'


def test_encipher_message():
    enciphered = keyword_encipher('test message', 'bayes') 
    expected = 'rsqr ksqqbds'
    assert enciphered == expected

    enciphered = keyword_encipher('test message', 'bayes', KeywordWrapAlphabet.from_a) 
    expected = 'rsqr ksqqbds'
    assert enciphered == expected

    enciphered = keyword_encipher('test message', 'bayes', KeywordWrapAlphabet.from_last) 
    expected = 'lskl dskkbus'
    assert enciphered == expected

    enciphered = keyword_encipher('test message', 'bayes', KeywordWrapAlphabet.from_largest) 
    expected = 'qspq jsppbcs'
    assert enciphered == expected


def test_decipher_message():
    plaintext = 'test message'
    for key in ['bayes', 'samplekey']:
        for wrap in KeywordWrapAlphabet:
            enciphered = keyword_encipher(plaintext, key, wrap)
            deciphered = keyword_decipher(enciphered, key, wrap)
            assert deciphered == plaintext


def test_keyword_break():
    plaintext = 'this is a test message for the keyword breaking routine'
    expected_key = 'elephant'
    expected_wrap = KeywordWrapAlphabet.from_last
    ciphertext = keyword_encipher(plaintext, expected_key, expected_wrap)
    (key, wrap), score = keyword_break(ciphertext, 
        wordlist=['cat', 'elephant', 'kangaroo'])
    assert key == expected_key
    assert wrap == expected_wrap
    assert score == pytest.approx(Pletters(sanitise(plaintext)))

def test_keyword_break_mp():
    plaintext = 'this is a test message for the keyword breaking routine'
    expected_key = 'elephant'
    expected_wrap = KeywordWrapAlphabet.from_last
    ciphertext = keyword_encipher(plaintext, expected_key, expected_wrap)
    (key, wrap), score = keyword_break_mp(ciphertext, 
        wordlist=['cat', 'elephant', 'kangaroo'])
    assert key == expected_key
    assert wrap == expected_wrap
    assert score == pytest.approx(Pletters(sanitise(plaintext)))


# def test_simulated_annealing_break():
#     # random.seed(0)
#     plaintext = '''You will rejoice to hear that no disaster has accompanied the
#     commencement of an enterprise which you have regarded with such evil
#     forebodings.  I arrived here yesterday, and my first task is to assure
#     my dear sister of my welfare and increasing confidence in the success
#     of my undertaking.

#     I am already far north of London, and as I walk in the streets of
#     Petersburgh, I feel a cold northern breeze play upon my cheeks, which
#     braces my nerves and fills me with delight.  Do you understand this
#     feeling?  This breeze, which has travelled from the regions towards
#     which I am advancing, gives me a foretaste of those icy climes.
#     Inspirited by this wind of promise, my daydreams become more fervent
#     and vivid.  

#      I try in vain to be persuaded that the pole is the seat of
#     frost and desolation; it ever presents itself to my imagination as the
#     region of beauty and delight.  There, Margaret, the sun is for ever
#     visible, its broad disk just skirting the horizon and diffusing a
#     perpetual splendour.  There—for with your leave, my sister, I will put
#     some trust in preceding navigators—there snow and frost are banished;
#     and, sailing over a calm sea, we may be wafted to a land surpassing in
#     wonders and in beauty every region hitherto discovered on the habitable
#     globe.  

#     Its productions and features may be without example, as the
#     phenomena of the heavenly bodies undoubtedly are in those undiscovered
#     solitudes.  What may not be expected in a country of eternal light?  I
#     may there discover the wondrous power which attracts the needle and may
#     regulate a thousand celestial observations that require only this
#     voyage to render their seeming eccentricities consistent for ever.  I
#     shall satiate my ardent curiosity with the sight of a part of the world
#     never before visited, and may tread a land never before imprinted by
#     the foot of man. These are my enticements, and they are sufficient to
#     conquer all fear of danger or death and to induce me to commence this
#     laborious voyage with the joy a child feels when he embarks in a little
#     boat, with his holiday mates, on an expedition of discovery up his
#     native river. 

#     But supposing all these conjectures to be false, you cannot contest the
#     inestimable benefit which I shall confer on all mankind, to the last
#     generation, by discovering a passage near the pole to those countries, to
#     reach which at present so many months are requisite; or by ascertaining the
#     secret of the magnet, which, if at all possible, can only be effected by an
#     undertaking such as mine.'''

#     expected_key = keyword_cipher_alphabet_of('abced')
#     ciphertext = keyword_encipher(sanitise(plaintext), expected_key)
#     expected_score = Ptrigrams(sanitise(plaintext))
#     actual_key, actual_score = monoalphabetic_sa_break(ciphertext, 
#         plain_alphabet=string.ascii_lowercase,
#         cipher_alphabet=string.ascii_lowercase,
#         workers=10, max_iterations=1000, 
#         fitness=Ptrigrams
#         )
#     assert expected_key == actual_key
#     assert expected_score == pytest.approx(actual_score)
