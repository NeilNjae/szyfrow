"""Descriptions of English, used for building language models. 

Language models are for understanding what English looks like, for help with 
cipher breaking.

* `count_1l.txt`: counts of single letters
* `count_2l.txt`: counts of pairs letters, bigrams
* `count_3l.txt`: counts of triples of letters, triagrams
* `words.txt`: a dictionary of words, used for keyword-based cipher breaking.
  These words should only contain characters cointained in 
  `string.ascii_letters`.

See [`szyfrow/language_models`](../support/language_models.html) for how these files are used.
"""