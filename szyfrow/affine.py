"""Enciphering and deciphering using the [affine cipher](https://en.wikipedia.org/wiki/Affine_cipher). 
Also attempts to break messages that use an affine cipher.

The affine cipher operates one letter at a time. It converts each letter to a 
number, then enciphers that number using a multiplier and a number. The result 
is taken mod 26 and converted back into a letter.

For a multiplier _m_ and adder _a_, a letter converted to number _x_ is 
enciphered as _E(x)_ = (_m_ _x_ + _a_) mod 26. Deciphering uses the modular 
inverse of _m_, _m_⁻¹, so that _D(x)_ = _m_⁻¹ (_x_ - _a_) mod 26.

If `one_based` is `True`, the conversion between letters and numbers maps 
'a' → 1, 'b' → 2, … 'z'→ 26 and the `mod` function is adjusted to keep 
numbers in this range during enciphering and deciphering. If `one_based` is 
`False`, the conversion maps 'a' → 0, 'b' → 1, … 'z'→ 25 and `mod` behaves
normally.
"""

from szyfrow.support.utilities import *
from szyfrow.support.language_models import *

modular_division_table = {
    (multiplier, (multiplier * plaintext) % 26): plaintext
    for plaintext in range(26) 
    for multiplier in range(26)
    }


def affine_encipher_letter(accented_letter, multiplier=1, adder=0, one_based=True):
    """Encipher a letter, given a multiplier and adder.

    Accented version of latin letters (such as é and ö) are converted to their
    non-accented versions before encryption.
    
    >>> cat(affine_encipher_letter(l, 3, 5, True) \
            for l in string.ascii_letters)
    'hknqtwzcfiloruxadgjmpsvybeHKNQTWZCFILORUXADGJMPSVYBE'
    >>> cat(affine_encipher_letter(l, 3, 5, False) \
            for l in string.ascii_letters)
    'filoruxadgjmpsvybehknqtwzcFILORUXADGJMPSVYBEHKNQTWZC'
    """
    letter = unaccent(accented_letter)
    if letter in string.ascii_letters:
        letter_number = pos(letter)
        if one_based: letter_number += 1
        cipher_number = (letter_number * multiplier + adder) % 26
        if one_based: cipher_number -= 1
        if letter in string.ascii_uppercase:
            return unpos(cipher_number).upper()
        else:
            return unpos(cipher_number)
    else:
        return letter

def affine_decipher_letter(letter, multiplier=1, adder=0, one_based=True):
    """Encipher a letter, given a multiplier and adder
    
    >>> cat(affine_decipher_letter(l, 3, 5, True) \
            for l in 'hknqtwzcfiloruxadgjmpsvybeHKNQTWZCFILORUXADGJMPSVYBE')
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    >>> cat(affine_decipher_letter(l, 3, 5, False) \
            for l in 'filoruxadgjmpsvybehknqtwzcFILORUXADGJMPSVYBEHKNQTWZC')
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    """
    if letter in string.ascii_letters:
        cipher_number = pos(letter)
        if one_based: cipher_number += 1
        plaintext_number = ( 
            modular_division_table[multiplier, (cipher_number - adder) % 26]
            )
        if one_based: plaintext_number -= 1
        if letter in string.ascii_uppercase:
            return unpos(plaintext_number).upper()
        else:
            return unpos(plaintext_number) 
    else:
        return letter

def affine_encipher(message, multiplier=1, adder=0, one_based=True):
    """Encipher a message
    
    >>> affine_encipher('hours passed during which jerico tried every ' \
           'trick he could think of', 15, 22, True)
    'lmyfu bkuusd dyfaxw claol psfaom jfasd snsfg jfaoe ls omytd jlaxe mh'
    """
    enciphered = [affine_encipher_letter(l, multiplier, adder, one_based) 
                  for l in message]
    return cat(enciphered)

def affine_decipher(message, multiplier=1, adder=0, one_based=True):
    """Decipher a message
    
    >>> affine_decipher('lmyfu bkuusd dyfaxw claol psfaom jfasd snsfg ' \
           'jfaoe ls omytd jlaxe mh', 15, 22, True)
    'hours passed during which jerico tried every trick he could think of'
    """
    enciphered = [affine_decipher_letter(l, multiplier, adder, one_based) 
                  for l in message]
    return cat(enciphered)



def affine_break(message, fitness=Pletters):
    """Breaks an affine cipher using frequency analysis.

    It tries all possible combinations of multiplier, adder, and one_based,
    scores the fitness of the text decipherd with each combination, and returns
    the key that produces the most fit deciphered text.

    >>> affine_break('lmyfu bkuusd dyfaxw claol psfaom jfasd snsfg jfaoe ls ' \
          'omytd jlaxe mh jm bfmibj umis hfsul axubafkjamx. ls kffkxwsd jls ' \
          'ofgbjmwfkiu olfmxmtmwaokttg jlsx ls kffkxwsd jlsi zg tsxwjl. jlsx ' \
          'ls umfjsd jlsi zg hfsqysxog. ls dmmdtsd mx jls bats mh bkbsf. ls ' \
          'bfmctsd kfmyxd jls lyj, mztanamyu xmc jm clm cku tmmeaxw kj lai ' \
          'kxd clm ckuxj.') # doctest: +ELLIPSIS
    ((15, 22, True), -340.601181913...)
    """
    sanitised_message = sanitise(message)
    best_multiplier = 0
    best_adder = 0
    best_one_based = True
    best_fit = float("-inf")
    for one_based in [True, False]:
        for multiplier in [x for x in range(1, 26, 2) if x != 13]:
            for adder in range(26):
                plaintext = affine_decipher(sanitised_message,
                                            multiplier, adder, one_based)
                fit = fitness(plaintext)
                if fit > best_fit:
                    best_fit = fit
                    best_multiplier = multiplier
                    best_adder = adder
                    best_one_based = one_based

    return (best_multiplier, best_adder, best_one_based), best_fit
