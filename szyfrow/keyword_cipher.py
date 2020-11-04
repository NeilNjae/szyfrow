"""Monoalphabetic substitution ciphers, mainly done by keyword. Enciphering
and deciphering, and a couple of ways to break these ciphers.
"""
from enum import Enum
import multiprocessing
import math
from szyfrow.support.utilities import *
from szyfrow.support.language_models import *


class KeywordWrapAlphabet(Enum):
    """Ways to list the rest of the alphabet after use of a keyword.

    * `from_a` : continue the alphabet from 'a': `bayescdfg...`
    * `from_last`: continue from the last letter of the keyword: 
        `bayestuvwxyzcdf...`
    * `from_largest`: continue from the "largest" letter of the keyword:
        `bayeszcdfg...`
    """
    from_a = 1
    from_last = 2
    from_largest = 3


def keyword_cipher_alphabet_of(keyword, wrap_alphabet=KeywordWrapAlphabet.from_a):
    """Find the cipher alphabet given a keyword.

    [`wrap_alphabet`](#szyfrow.keyword_cipher.KeywordWrapAlphabet) controls 
    how the rest of the alphabet is added after the keyword.

    >>> keyword_cipher_alphabet_of('bayes')
    'bayescdfghijklmnopqrtuvwxz'
    >>> keyword_cipher_alphabet_of('bayes', KeywordWrapAlphabet.from_a)
    'bayescdfghijklmnopqrtuvwxz'
    >>> keyword_cipher_alphabet_of('bayes', KeywordWrapAlphabet.from_last)
    'bayestuvwxzcdfghijklmnopqr'
    >>> keyword_cipher_alphabet_of('bayes', KeywordWrapAlphabet.from_largest)
    'bayeszcdfghijklmnopqrtuvwx'
    """
    if wrap_alphabet == KeywordWrapAlphabet.from_a:
        cipher_alphabet = cat(deduplicate(sanitise(keyword) + 
                                              string.ascii_lowercase))
    else:
        if wrap_alphabet == KeywordWrapAlphabet.from_last:
            last_keyword_letter = deduplicate(sanitise(keyword))[-1]
        else:
            last_keyword_letter = sorted(sanitise(keyword))[-1]
        last_keyword_position = string.ascii_lowercase.find(
            last_keyword_letter) + 1
        cipher_alphabet = cat(
            deduplicate(sanitise(keyword) + 
                        string.ascii_lowercase[last_keyword_position:] + 
                        string.ascii_lowercase))
    return cipher_alphabet


def keyword_encipher(message, keyword, wrap_alphabet=KeywordWrapAlphabet.from_a):
    """Enciphers a message with a keyword substitution cipher.
    wrap_alphabet controls how the rest of the alphabet is added
    after the keyword.
    0 : from 'a'
    1 : from the last letter in the sanitised keyword
    2 : from the largest letter in the sanitised keyword

    >>> keyword_encipher('test message', 'bayes')
    'rsqr ksqqbds'
    >>> keyword_encipher('test message', 'bayes', KeywordWrapAlphabet.from_a)
    'rsqr ksqqbds'
    >>> keyword_encipher('test message', 'bayes', KeywordWrapAlphabet.from_last)
    'lskl dskkbus'
    >>> keyword_encipher('test message', 'bayes', KeywordWrapAlphabet.from_largest)
    'qspq jsppbcs'
    """
    cipher_alphabet = keyword_cipher_alphabet_of(keyword, wrap_alphabet)
    cipher_translation = ''.maketrans(string.ascii_lowercase, cipher_alphabet)
    return unaccent(message).lower().translate(cipher_translation)

def keyword_decipher(message, keyword, wrap_alphabet=KeywordWrapAlphabet.from_a):
    """Deciphers a message with a keyword substitution cipher.
    wrap_alphabet controls how the rest of the alphabet is added
    after the keyword.
    0 : from 'a'
    1 : from the last letter in the sanitised keyword
    2 : from the largest letter in the sanitised keyword
    
    >>> keyword_decipher('rsqr ksqqbds', 'bayes')
    'test message'
    >>> keyword_decipher('rsqr ksqqbds', 'bayes', KeywordWrapAlphabet.from_a)
    'test message'
    >>> keyword_decipher('lskl dskkbus', 'bayes', KeywordWrapAlphabet.from_last)
    'test message'
    >>> keyword_decipher('qspq jsppbcs', 'bayes', KeywordWrapAlphabet.from_largest)
    'test message'
    """
    cipher_alphabet = keyword_cipher_alphabet_of(keyword, wrap_alphabet)
    cipher_translation = ''.maketrans(cipher_alphabet, string.ascii_lowercase)
    return message.lower().translate(cipher_translation)


def keyword_break_single_thread(message, wordlist=None, fitness=Pletters):
    """Breaks a keyword substitution cipher using a dictionary and
    frequency analysis.

    If `wordlist` is not specified, use 
    [`szyfrow.support.langauge_models.keywords`](support/language_models.html#szyfrow.support.language_models.keywords).

    >>> keyword_break(keyword_encipher('this is a test message for the ' \
          'keyword decipherment', 'elephant', KeywordWrapAlphabet.from_last), \
          wordlist=['cat', 'elephant', 'kangaroo']) # doctest: +ELLIPSIS
    (('elephant', <KeywordWrapAlphabet.from_last: 2>), -52.834575011...)
    """
    if wordlist is None:
      wordlist = keywords

    best_keyword = ''
    best_wrap_alphabet = True
    best_fit = float("-inf")
    for wrap_alphabet in KeywordWrapAlphabet:
        for keyword in wordlist:
            plaintext = keyword_decipher(message, keyword, wrap_alphabet)
            fit = fitness(plaintext)
            if fit > best_fit:
                best_fit = fit
                best_keyword = keyword
                best_wrap_alphabet = wrap_alphabet
    return (best_keyword, best_wrap_alphabet), best_fit

def keyword_break(message, wordlist=None, fitness=Pletters,
                     number_of_solutions=1, chunksize=500):
    """Breaks a keyword substitution cipher using a dictionary and
    frequency analysis.

    If `wordlist` is not specified, use 
    [`szyfrow.support.langauge_models.keywords`](support/language_models.html#szyfrow.support.language_models.keywords).


    >>> keyword_break_mp(keyword_encipher('this is a test message for the ' \
          'keyword decipherment', 'elephant', KeywordWrapAlphabet.from_last), \
          wordlist=['cat', 'elephant', 'kangaroo']) # doctest: +ELLIPSIS
    (('elephant', <KeywordWrapAlphabet.from_last: 2>), -52.834575011...)
    >>> keyword_break_mp(keyword_encipher('this is a test message for the ' \
          'keyword decipherment', 'elephant', KeywordWrapAlphabet.from_last), \
          wordlist=['cat', 'elephant', 'kangaroo'], \
          number_of_solutions=2) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    [(('elephant', <KeywordWrapAlphabet.from_last: 2>), -52.834575011...), 
    (('elephant', <KeywordWrapAlphabet.from_largest: 3>), -52.834575011...)]
    """
    if wordlist is None:
        wordlist = keywords

    with multiprocessing.Pool() as pool:
        helper_args = [(message, word, wrap, fitness)
                       for word in wordlist
                       for wrap in KeywordWrapAlphabet]
        # Gotcha: the helper function here needs to be defined at the top level
        #   (limitation of Pool.starmap)
        breaks = pool.starmap(keyword_break_worker, helper_args, chunksize)
        if number_of_solutions == 1:
            return max(breaks, key=lambda k: k[1])
        else:
            return sorted(breaks, key=lambda k: k[1], reverse=True)[:number_of_solutions]

def keyword_break_worker(message, keyword, wrap_alphabet, fitness):
    plaintext = keyword_decipher(message, keyword, wrap_alphabet)
    fit = fitness(plaintext)
    return (keyword, wrap_alphabet), fit


def monoalphabetic_break_hillclimbing_single(message, 
                              max_iterations=20000,
                              plain_alphabet=None, 
                              cipher_alphabet=None, 
                              swap_index_finder=None,
                              fitness=Pletters, chunksize=1):
    """Break a monalphabetic substitution cipher using hillclimbing to
    guess the keyword. Hillclimbing is done by using the simulated annealing
    approach with a temperature of zero.

    This version uses a single worker.
    """
    return monoalphabetic_sa_break(message, 
                              workers=1, 
                              initial_temperature=0,
                              max_iterations=max_iterations,
                              plain_alphabet=plain_alphabet, 
                              cipher_alphabet=cipher_alphabet, 
                              swap_index_finder=swap_index_finder,
                              fitness=fitness, chunksize=chunksize)


def monoalphabetic_break_hillclimbing(message, 
                              workers=10, 
                              max_iterations=20000,
                              plain_alphabet=None, 
                              cipher_alphabet=None, 
                              swap_index_finder=None,
                              fitness=Pletters, chunksize=1):
    """Break a monalphabetic substitution cipher using hillclimbing to
    guess the keyword. Hillclimbing is done by using the simulated annealing
    approach with a temperature of zero.

    This version uses a several workers.
    """
    return monoalphabetic_sa_break(message, 
                              workers=workers, 
                              initial_temperature=0,
                              max_iterations=max_iterations,
                              plain_alphabet=plain_alphabet, 
                              cipher_alphabet=cipher_alphabet, 
                              swap_index_finder=swap_index_finder,
                              fitness=fitness, chunksize=chunksize)


def gaussian_swap_index(a):
    """Return an index to use as the partner of `a` in a swap. The partners
    are drawn from a Gaussian distribution.
    """
    return (a + int(random.gauss(0, 4))) % 26

def uniform_swap_index(a):
    """Return an index to use as the partner of `a` in a swap. The partners
    are drawn from a uniform distribution.
    """
    return random.randrange(26)

def monoalphabetic_sa_break(message, workers=10, 
                              initial_temperature=200,
                              max_iterations=20000,
                              plain_alphabet=None, 
                              cipher_alphabet=None, 
                              swap_index_finder=None,
                              fitness=Ptrigrams, chunksize=1):
    """Break a monalphabetic substitution cipher using simulated annealing to
    guess the keyword. This function just sets up a stable of workers who
    do the actual work, implemented as 
    `szyfrow.keyword_cipher.monoalphabetic_sa_break_worker`.

    See a [post on simulated annealing](https://work.njae.me.uk/2019/07/08/simulated-annealing-and-breaking-substitution-ciphers/)
    for detail on how this works.
    """
    worker_args = []
    ciphertext = sanitise(message)
    if swap_index_finder is None:
        swap_index_finder = gaussian_swap_index
        
    for i in range(workers):
        if plain_alphabet is None:
            used_plain_alphabet = string.ascii_lowercase
        else:
            used_plain_alphabet = plain_alphabet
        if cipher_alphabet is None:
            used_cipher_alphabet = list(string.ascii_lowercase)
            random.shuffle(used_cipher_alphabet)
            used_cipher_alphabet = cat(used_cipher_alphabet)
        else:
            used_cipher_alphabet = cipher_alphabet
        # if not plain_alphabet:
        #     plain_alphabet = string.ascii_lowercase
        # if not cipher_alphabet:
        #     cipher_alphabet = list(string.ascii_lowercase)
        #     random.shuffle(cipher_alphabet)
        #     cipher_alphabet = cat(cipher_alphabet)
        worker_args.append((ciphertext, used_plain_alphabet, used_cipher_alphabet, 
                            swap_index_finder,
                            initial_temperature, max_iterations, fitness,
                            i))
    with multiprocessing.Pool() as pool:
        breaks = pool.starmap(monoalphabetic_sa_break_worker,
                              worker_args, chunksize)
    return max(breaks, key=lambda k: k[1])


def monoalphabetic_sa_break_worker(message, plain_alphabet, cipher_alphabet, 
                                     swap_index_finder,
                                     t0, max_iterations, fitness,
                                     logID):
    """One thread of a simulated annealing run. 
    See a [post on simulated annealing](https://work.njae.me.uk/2019/07/08/simulated-annealing-and-breaking-substitution-ciphers/)
    for detail on how this works.
    """
    def swap(letters, i, j):
        if i > j:
            i, j = j, i
        if i == j:
            return letters
        else:
            return (letters[:i] + letters[j] + letters[i+1:j] + letters[i] +
                    letters[j+1:])
    
    temperature = t0

    dt = t0 / (0.9 * max_iterations)
    
    current_alphabet = cipher_alphabet
    alphabet = current_alphabet
    cipher_translation = ''.maketrans(current_alphabet, plain_alphabet)
    plaintext = message.translate(cipher_translation)
    current_fitness = fitness(plaintext)

    best_alphabet = current_alphabet
    best_fitness = current_fitness
    best_plaintext = plaintext
    
    # print('starting for', max_iterations)
    for i in range(max_iterations):
        swap_a = random.randrange(26)
        # swap_b = (swap_a + int(random.gauss(0, 4))) % 26
        swap_b = swap_index_finder(swap_a)
        alphabet = swap(current_alphabet, swap_a, swap_b)
        cipher_translation = ''.maketrans(alphabet, plain_alphabet)
        plaintext = message.translate(cipher_translation)
        new_fitness = fitness(plaintext)
        try:
            sa_chance = math.exp((new_fitness - current_fitness) / temperature)
        except (OverflowError, ZeroDivisionError):
            # print('exception triggered: new_fit {}, current_fit {}, temp {}'.format(new_fitness, current_fitness, temperature))
            sa_chance = 0
        if (new_fitness > current_fitness or random.random() < sa_chance):
            current_fitness = new_fitness
            current_alphabet = alphabet
            
        if current_fitness > best_fitness:
            best_alphabet = current_alphabet
            best_fitness = current_fitness
            best_plaintext = plaintext

        temperature = max(temperature - dt, 0.001)

    return best_alphabet, best_fitness # current_alphabet, current_fitness

if __name__ == "__main__":
    import doctest
