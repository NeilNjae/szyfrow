import pytest
import string 

from szyfrow.support.language_models import *

def test_transpositions_of():
    assert transpositions_of('clever') == (0, 2, 1, 4, 3)
    assert transpositions_of('fred') == (3, 2, 0, 1)
    assert transpositions_of((3, 2, 0, 1)) == (3, 2, 0, 1)

def test_ngrams():
    assert ngrams(sanitise('the quick brown fox'), 2) == ['th', 'he', 'eq', 
        'qu', 'ui', 'ic', 'ck', 'kb', 'br', 'ro', 'ow', 'wn', 
        'nf', 'fo', 'ox']
    assert ngrams(sanitise('the quick brown fox'), 4) == ['theq', 'hequ', 
        'equi', 'quic', 'uick', 'ickb', 'ckbr', 'kbro', 'brow', 
        'rown', 'ownf', 'wnfo', 'nfox']
    