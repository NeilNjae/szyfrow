import pytest
import string 

from szyfrow.cadenus import *
from szyfrow.support.utilities import *

def test_keycolumn():
    assert make_cadenus_keycolumn()['a'] == 0
    assert make_cadenus_keycolumn()['b'] == 1
    assert make_cadenus_keycolumn()['c'] == 2
    assert make_cadenus_keycolumn()['v'] == 21
    assert make_cadenus_keycolumn()['w'] == 21
    assert make_cadenus_keycolumn()['z'] == 24
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['a'] == 1
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['b'] == 0
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['c'] == 24
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['i'] == 18
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['j'] == 18
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['v'] == 6
    assert make_cadenus_keycolumn(doubled_letters='ij', start='b', 
        reverse=True)['z'] == 2


def test_encipher_message():
    plaintext = sanitise('''Whoever has made a voyage up the Hudson must 
        remember the Kaatskill mountains. They are a dismembered branch of 
        the great''')
    keycol = make_cadenus_keycolumn(doubled_letters='vw', start='a', reverse=True)
    ciphertext = cadenus_encipher(plaintext, 'wink', keycol)
    expected = 'antodeleeeuhrsidrbhmhdrrhnimefmthgeaetakseomehetyaasuvoyegrastmmuuaeenabbtpchehtarorikswosmvaleatned'
    assert ciphertext == expected

    plaintext = sanitise('''a severe limitation on the usefulness of the 
        cadenus is that every message must be a multiple of twenty-five 
        letters long''')
    ciphertext = cadenus_encipher(plaintext, 'easy', keycol)
    expected = 'systretomtattlusoatleeesfiyheasdfnmschbhneuvsnpmtofarenuseieeieltarlmentieetogevesitfaisltngeeuvowul'
    assert ciphertext == expected


def test_decipher_message():
    plaintext = sanitise('''Whoever has made a voyage up the Hudson must 
        remember the Kaatskill mountains. They are a dismembered branch of 
        the great''')
    keycol = make_cadenus_keycolumn(doubled_letters='vw', start='a', reverse=True)
    for key in ['wink', 'easy']: 
        enciphered = cadenus_encipher(plaintext, key, keycol)
        deciphered = cadenus_decipher(enciphered, key, keycol)
        assert deciphered == plaintext


def test_cadenus_break():
    plaintext = sanitise('''You will rejoice to hear that no disaster has accompanied the
commencement of an enterprise which you have regarded with such evil
forebodings.  I arrived here yesterday, and my first task is to assure
my dear sister of my welfare and increasing confidence in the success
of my undertaking.

I am already far north of London, and as I walk in the streets of
Petersburgh, I feel a cold northern breeze play upon my cheeks, which
braces my nerves and fills me with delight.  Do you understand this
feeling?  This breeze, which has travelled from the regions towards
which I am advancing, gives me a foretaste of those icy climes.
Inspirited by this wind of promise, my daydreams become more fervent
and vivid.  

I try in vain to be persuaded that the pole is the seat of
frost and desolation; it ever presents itself to my imagination as the
region of beauty and delight.  There, Margaret, the sun is for ever
visible, its broad disk just skirting the horizon and diffusing a
perpetual splendour.  There—for with your leave, my sister, I will put
some trust in preceding navigators—there snow and frost are banished;
and, sailing over a calm sea, we may be wafted to a land surpassing in
wonders and in beauty every region hitherto discovered on the habitable
globe.  

Its productions and features may be without example, as the
phenomena of the heavenly bodies undoubtedly are in those undiscovered
solitudes.  What may not be expected in a country of eternal light?  I
may there discover the wondrous power which attracts the needle and may
regulate a thousand celestial observations that require only this
voyage to render their seeming eccentricities consistent for ever.  I
shall satiate my ardent curiosity with the sight of a part of the world
never before visited, and may tread a land never before imprinted by
the foot of man. These are my enticements, and they are sufficient to
conquer all fear of danger or death and to induce me to commence this
laborious voyage with the joy a child feels when he embarks in a little
boat, with his holiday mates, on an expedition of discovery up his
native river. '''
)
    expected_key = 'swashbuckling'
    chunk_len = len(transpositions_of(expected_key)) * 25
    target = plaintext + pad(len(plaintext), chunk_len, 'a')
    expected_score = Ptrigrams(target)
    expected_keycol = make_cadenus_keycolumn(doubled_letters='vw', start='a', 
        reverse=True)

    ciphertext = cadenus_encipher(plaintext, expected_key, expected_keycol)
    
    dictionary = ['clearinghouse', 'computerising', 'counterclaims', 
        'housewarmings',  'intravenously', 'liquefactions', 'somersaulting', 
        'sportsmanlike', 'swashbuckling']

    # dictionary = ['swashbuckling']

    (key, keycol), score = cadenus_break(ciphertext, wordlist=dictionary, 
        fitness=Ptrigrams)

    assert key == expected_key
    assert keycol == expected_keycol
    assert score == pytest.approx(expected_score)
