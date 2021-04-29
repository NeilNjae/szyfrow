"""Simple (mainly manual) ciphers, and routines for enciphering, deciphering, 
and breaking messages created with them.

The ciphers implemented here are mostly ones that predate mechanical cipher
systems. The most complex cipher is the Enigma of World War II.

Each cipher is presented with functions to encipher, decipher, and 
automatically break messages with that cipher.

Most of the time, messages are broken by brute-force trying each possible key
and scoring the resulting deciphered message using a bag-of-words probability
measure (or a bag-of-bigrams, or a bag-of-trigrams).

You can find more information on the ciphers and how they are implemented in
the [codes and ciphers area of my blog](https://work.njae.me.uk/tag/codes-and-ciphers/).

Ciphers work on messages encoded with the 26 letters of the Latin alphabet,
without accents (the letters contained in the `string.ascii_letters` constant).
Most of the ciphers convert letters to lowercase, strip accents from letters,
and drop all other characters (such as spaces and punctuation).

`szyfrow.support.text_prettify` contains functions to make the output easier
to read, such as automatically recovering word boundaries.

The name comes from the Polish cipher bureau, the Biuro Szyfrów, who were 
breaking Enigma ciphers by hand before World War II.
"""