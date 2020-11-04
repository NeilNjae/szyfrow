"""A simulator for Enigma machines.

See `szyfrow.bombe.Bombe` for an implementation of the Bombe to break Enigma
messages.

Specification from [Codes and Ciphers](http://www.codesandciphers.org.uk/enigma/rotorspec.htm) page.

Example Enigma machines from [Louise Dale](http://enigma.louisedade.co.uk/enigma.html) (full simulation) and [EnigmaCo](http://enigmaco.de/enigma/enigma.html) (good animation of the wheels, but no ring settings).

There's also the nice Enigma simulator for Android by [Franklin Heath](https://franklinheath.co.uk/2012/02/04/our-first-app-published-enigma-simulator/), available on the [Google Play store](https://play.google.com/store/apps/details?id=uk.co.franklinheath.enigmasim&hl=en_GB).
"""

import string
import collections
import multiprocessing
import itertools

from szyfrow.support.utilities import *

# # Some convenience functions

# cat = ''.join

# def clean(text): return cat(l.lower() for l in text if l in string.ascii_letters)

# def pos(letter): 
#     if letter in string.ascii_lowercase:
#         return ord(letter) - ord('a')
#     elif letter in string.ascii_uppercase:
#         return ord(letter) - ord('A')
#     else:
#         return ''
    
# def unpos(number): return chr(number % 26 + ord('a'))


wheel_i_spec = 'ekmflgdqvzntowyhxuspaibrcj'
wheel_ii_spec = 'ajdksiruxblhwtmcqgznpyfvoe'
wheel_iii_spec = 'bdfhjlcprtxvznyeiwgakmusqo'
wheel_iv_spec = 'esovpzjayquirhxlnftgkdcmwb'
wheel_v_spec = 'vzbrgityupsdnhlxawmjqofeck'
wheel_vi_spec = 'jpgvoumfyqbenhzrdkasxlictw'
wheel_vii_spec = 'nzjhgrcxmyswboufaivlpekqdt'
wheel_viii_spec = 'fkqhtlxocbjspdzramewniuygv'
beta_wheel_spec = 'leyjvcnixwpbqmdrtakzgfuhos'
gamma_wheel_spec = 'fsokanuerhmbtiycwlqpzxvgjd'

wheel_i_notches = ['q']
wheel_ii_notches = ['e']
wheel_iii_notches = ['v']
wheel_iv_notches = ['j']
wheel_v_notches = ['z']
wheel_vi_notches = ['z', 'm']
wheel_vii_notches = ['z', 'm']
wheel_viii_notches = ['z', 'm']

reflector_b_spec = 'ay br cu dh eq fs gl ip jx kn mo tz vw'
reflector_c_spec = 'af bv cp dj ei go hy kr lz mx nw tq su'



class LetterTransformer(object):
    """A generic substitution cipher, that has different transforms in the 
    forward and backward directions. It requires that the transforms for all
    letters by provided.

    A `transform` is a list of letter pairs, like `[('a', 'b'), ('c', 'd')]`.
    That would say that, in the forward direction `a` goes to `b` and 
    `c` goes to `d`. In the backward direction, `b` goes to `a` and `d` goes
    to `c`. 
    """
    def __init__(self, specification, raw_transform=False):
        """Validate and create a new transformer. The transform is parsed by
        `LetterTransformer.parse_specification` unless `raw_transform` is `True`
        """
        if raw_transform:
            transform = specification
        else:
            transform = self.parse_specification(specification)
        self.validate_transform(transform)
        self.make_transform_map(transform)
    
    def parse_specification(self, specification):
        """Turn a `specification` string into a transform, by zipping it
        with ASCII lowercase letters to generate the pairs. This assumes that
        the `specification` defines the destination of the forward transform.
        """
        return list(zip(string.ascii_lowercase, sanitise(specification)))
        # return specification
    
    def validate_transform(self, transform):
        """Checks that a transform is valid (every letter is mapped to 
        exactly one other letter, in both directions).
        """
        if len(transform) != 26:
            raise ValueError("Transform specification has {} pairs, requires 26".
                format(len(transform)))
        for p in transform:
            if len(p) != 2:
                raise ValueError("Not all mappings in transform "
                    "have two elements")
        if len(set([p[0] for p in transform])) != 26:
            raise ValueError("Transform specification must list 26 origin letters") 
        if len(set([p[1] for p in transform])) != 26:
            raise ValueError("Transform specification must list 26 destination letters") 

    def make_empty_transform(self):
        """An empty transform is one that maps every letter to 'a'.
        """
        self.forward_map = [0] * 26
        self.backward_map = [0] * 26
            
    def make_transform_map(self, transform):
        """Create `forward_map` and `backward_map` from `transform`. The maps
        work on letter positions, not letter values. This makes the arithmetic
        for wheels much easier.
        """
        self.make_empty_transform()
        for p in transform:
            self.forward_map[pos(p[0])] = pos(p[1])
            self.backward_map[pos(p[1])] = pos(p[0])
        return self.forward_map, self.backward_map
    
    def forward(self, letter):
        """Apply a map in the forward direction.
        """
        if letter in string.ascii_lowercase:
            return unpos(self.forward_map[pos(letter)])
        else:
            return ''
                
    def backward(self, letter):
        """Apply a map in the backward direction.
        """
        if letter in string.ascii_lowercase:
            return unpos(self.backward_map[pos(letter)])
        else:
            return ''


class Plugboard(LetterTransformer):
    """A plugboard, a type of letter transformer where forward and backward
    transforms are the same. If a letter isn't explicitly transformed, it is 
    kept as it is.
    """

    def parse_specification(self, specification):
        """Convert a specification into a transform. The specification is
        given as a list of letter pairs.
        """
        return [tuple(sanitise(p)) for p in specification.split()]
    
    def validate_transform(self, transform):
        """A set of pairs, of from-to. Does not require all 26 letters
        are in the transform.
        """
        for p in transform:
            if len(p) != 2:
                raise ValueError("Not all mappings in transform"
                    "have two elements")
    
    def make_empty_transform(self):
        """An empty transform maps every letter to itself.
        """
        self.forward_map = list(range(26))
        self.backward_map = list(range(26))
        
    def make_transform_map(self, transform):
        """Makes the maps for a plugboard. Ensures that if the pair ('a', 'b')
        is in the specification, the pair ('b', 'a') is also present.
        """
        expanded_transform = transform + [tuple(reversed(p)) for p in transform]
        return super(Plugboard, self).make_transform_map(expanded_transform)




class Reflector(Plugboard):
    """A reflector is a plugboard that requires 13 transforms.
    The 'plugboard' superclass ensures that all 13 transforms are also applied
    in reverse, making 26 transforms in all.
    """
    def validate_transform(self, transform):
        if len(transform) != 13:
            raise ValueError("Reflector specification has {} pairs, requires 13".
                format(len(transform)))
        if len(set([p[0] for p in transform] + 
                    [p[1] for p in transform])) != 26:
            raise ValueError("Reflector specification does not contain 26 letters")
        try:
            super(Reflector, self).validate_transform(transform)
        except ValueError as v:
            raise ValueError("Not all mappings in reflector have two elements")




class SimpleWheel(LetterTransformer):
    """A wheel is a transform that rotates.

    Looking from the right, letters go in sequence a-b-c clockwise around the 
    wheel. 

    The position of the wheel is the number of spaces anticlockwise the wheel
    has turned.

    Letter inputs and outputs are given relative to the frame holding the wheel,
    so if the wheel is advanced three places, an input of 'p' will enter the 
    wheel on the position under the wheel's 's' label.
    """
    def __init__(self, transform, position='a', raw_transform=False):
        super(SimpleWheel, self).__init__(transform, raw_transform)
        self.set_position(position)
        
    def __getattribute__(self,name):
        if name=='position_l':
            return unpos(self.position)
        else:
            return object.__getattribute__(self, name)
    
    def set_position(self, position):
        """Sets a wheel's position. If the `position` is a string, convert it
        to a number and set the position.
        """
        if isinstance(position, str):
            self.position = pos(position)
        else:
            self.position = position
    
    def forward(self, letter):
        """Give the transformed letter in the forward direction, accounting
        for the position of the wheel.
        """
        if letter in string.ascii_lowercase:
            return unpos((self.forward_map[(pos(letter) + self.position) % 26] - self.position))
        else:
            return ''
                
    def backward(self, letter):
        """Give the transformed letter in the backward direction, accounting
        for the position of the wheel.
        """
        if letter in string.ascii_lowercase:
            return unpos((self.backward_map[(pos(letter) + self.position) % 26] - self.position))
        else:
            return ''
        
    def advance(self):
        """Advance a wheel one position."""
        self.position = (self.position + 1) % 26



class Wheel(SimpleWheel):
    """A wheel with a movable ring.

    The ring holds the letters and the notches that turn other wheels. The core
    holds the wiring that does the transformation.

    The ring position is how many steps the core is turned relative to the ring.
    This is one-based, so a ring setting of 1 means the core and ring are 
    aligned.

    The position of the wheel is the position of the core (the transforms) 
    relative to the neutral position. 

    The position_l is the position of the ring, or what would be observed
    by the user of the Enigma machine. 

    The notch_positions are the number of advances of this wheel before it will 
    advance the next wheel.
    """
    def __init__(self, transform, ring_notch_letters, ring_setting=1, 
            position='a', raw_transform=False):
        self.ring_notch_letters = ring_notch_letters
        self.ring_setting = ring_setting
        super(Wheel, self).__init__(transform, position=position, 
            raw_transform=raw_transform)
        self.set_position(position)
        
    def __getattribute__(self,name):
        if name=='position_l':
            return unpos(self.position + self.ring_setting - 1)
        else:
            return object.__getattribute__(self, name)

    def set_position(self, position):
        if isinstance(position, str):
            self.position = (pos(position) - self.ring_setting + 1) % 26
        else:
            self.position = (position - self.ring_setting) % 26
        # # self.notch_positions = [(pos(p) - pos(position)) % 26  for p in self.ring_notch_letters]
        # self.notch_positions = [(pos(p) - (self.position + self.ring_setting - 1)) % 26  for p in self.ring_notch_letters]
        self.notch_positions = [(self.position + self.ring_setting - 1 - pos(p)) % 26  for p in self.ring_notch_letters]
        
    def advance(self):
        """Advance a wheel's core, then advance the ring position to match.
        """
        super(Wheel, self).advance()
        self.notch_positions = [(p + 1) % 26 for p in self.notch_positions]
        return self.position


class Enigma(object):
    """An Enigma machine.


    """
    def __init__(self, reflector_spec,
                 left_wheel_spec, left_wheel_notches,
                 middle_wheel_spec, middle_wheel_notches,
                 right_wheel_spec, right_wheel_notches,
                 left_ring_setting, middle_ring_setting, right_ring_setting,
                 plugboard_setting):
        self.reflector = Reflector(reflector_spec)
        self.left_wheel = Wheel(left_wheel_spec, left_wheel_notches, 
            ring_setting=left_ring_setting)
        self.middle_wheel = Wheel(middle_wheel_spec, middle_wheel_notches, 
            ring_setting=middle_ring_setting)
        self.right_wheel = Wheel(right_wheel_spec, right_wheel_notches, 
            ring_setting=right_ring_setting)
        self.plugboard = Plugboard(plugboard_setting)
        
    def __getattribute__(self,name):
        if name=='wheel_positions':
            return (self.left_wheel.position, 
                    self.middle_wheel.position, 
                    self.right_wheel.position
                    )
        elif name=='wheel_positions_l':
            return (self.left_wheel.position_l, 
                    self.middle_wheel.position_l, 
                    self.right_wheel.position_l
                    )
        elif name=='notch_positions':
            return (self.left_wheel.notch_positions, 
                    self.middle_wheel.notch_positions, 
                    self.right_wheel.notch_positions
                    )
        else:
            return object.__getattribute__(self, name)

    def set_wheels(self, left_wheel_position, middle_wheel_position, 
            right_wheel_position):
        """Set the Enigma's wheels to the specified positions.
        """
        self.left_wheel.set_position(left_wheel_position)
        self.middle_wheel.set_position(middle_wheel_position)
        self.right_wheel.set_position(right_wheel_position)
        
    def lookup(self, letter):
        """Lookup the enciphering of a letter, without advancing any wheels
        """
        a = self.plugboard.forward(letter)
        b = self.right_wheel.forward(a)
        c = self.middle_wheel.forward(b)
        d = self.left_wheel.forward(c)
        e = self.reflector.forward(d)
        f = self.left_wheel.backward(e)
        g = self.middle_wheel.backward(f)
        h = self.right_wheel.backward(g)
        i = self.plugboard.backward(h)
        return i
    
    def advance(self):
        """Advance the Enigma's wheels one step. The right wheel always
        advances. The middle and right wheels may advance if the notches
        line up correctly.
        """
        advance_middle = False
        advance_left = False
        if 0 in self.right_wheel.notch_positions:
            advance_middle = True
        if 0 in self.middle_wheel.notch_positions:
            advance_left = True
            advance_middle = True
        self.right_wheel.advance()
        if advance_middle: self.middle_wheel.advance()
        if advance_left: self.left_wheel.advance()
            
    def encipher_letter(self, letter):
        """Encipher a letter. Advance the Enigma machine, then lookup the
        encryption of a letter.
        """
        self.advance()
        return self.lookup(letter)
    
    def encipher(self, message):
        """Encipher a message."""
        enciphered = ''
        for letter in sanitise(message):
            enciphered += self.encipher_letter(letter)
        return enciphered

    decipher = encipher


# for i in range(26):
#     enigma.advance()
#     print('enigma.advance()')
#     print("assert(enigma.wheel_positions == {})".format(enigma.wheel_positions))
#     print("assert(cat(enigma.wheel_positions_l) == '{}')".format(cat(enigma.wheel_positions_l)))
#     print("assert(enigma.notch_positions == {})".format(enigma.notch_positions))
#     print("assert(cat(enigma.lookup(l) for l in string.ascii_lowercase) == '{}')".format(cat(enigma.lookup(l) for l in string.ascii_lowercase)))
#     print()


if __name__ == "__main__":
    import doctest
    # doctest.testmod(extraglobs={'lt': LetterTransformer(1, 'a')})
    doctest.testmod()

