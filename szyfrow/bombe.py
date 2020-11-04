"""A simulator for Bombe machines.

See `szyfrow.enigma.Enigma` for an implementation of the Enigma to create 
messages.

There is a good explanation of [how the bombe worked](http://www.ellsbury.com/enigmabombe.htm) 
by Graham Ellsbury.

In this implementation, there are *banks* of wires (what Ellsbury refers to
as "cables"), one bank for each position that appears in the menu. A bank 
comprises 26 wires, represented as a `dict` of `bool`s, depending on whether
that wire is live ("energised") or not.

The menu, derived from the crib, determines how the scramblers connect the 
banks. A `Connection` represents this.
"""

import string
import collections
import multiprocessing
import itertools
import logging

from szyfrow.enigma import *

__pdoc__ = {}

Signal = collections.namedtuple('Signal', ['bank', 'wire'])
__pdoc__['Signal'] = """Current propogation through the Bombe indicates that
this wire in this bank is live, and the effects need to be proogated further
through the machine.
"""
__pdoc__['Signal.bank'] = """The bank of a signal."""
__pdoc__['Signal.wire'] = """The wire of a signal."""

Connection = collections.namedtuple('Connection', ['banks', 'scrambler'])
__pdoc__['Connection'] = """A connection between banks made by a particular
scrambler (the scrambler state given by its position in the crib).
"""
__pdoc__['Connection.banks'] = """A list of two items, holding the bnaks of 
a connection."""
__pdoc__['Connection.scrambler'] = """The bnaks of a connection."""


MenuItem = collections.namedtuple('MenuIem', ['before', 'after', 'number'])
__pdoc__['MenuItem'] = """One item in the menu, derived from the crib.
"""
__pdoc__['MenuItem.before'] = "The letter before the transform (plaintext)."
__pdoc__['MenuItem.after'] = "The letter after the transform (ciphertext)."
__pdoc__['MenuItem.number'] = "The position of this item in the menu."


def make_menu(plaintext, ciphertext):
    """Create a menu from a crib: a given plaintext and ciphertext.

    No validation is done to ensure that this is a viable crib (e.g. no 
    checking for length, no checking that a letter is enciphered to itself).
    """
    return [MenuItem(p, c, i+1) 
            for i, (p, c) in enumerate(zip(plaintext, ciphertext))]


class Scrambler(object):
    """A scrambler is a collection of three `szyfrow.enigma.SimpleWheel`s.
    """
    def __init__(self, wheel1_spec, wheel2_spec, wheel3_spec, reflector_spec,
                 wheel1_pos='a', wheel2_pos='a', wheel3_pos='a'):
        self.wheel1 = SimpleWheel(wheel1_spec, position=wheel1_pos)
        self.wheel2 = SimpleWheel(wheel2_spec, position=wheel2_pos)
        self.wheel3 = SimpleWheel(wheel3_spec, position=wheel3_pos)
        self.reflector = Reflector(reflector_spec)
    
    __pdoc__['Scrambler.wheel_positions'] = """Return a 3-tuple of the wheel
    positions (as numbers)"""
    __pdoc__['Scrambler.wheel_positions_l'] = """Return a 3-tuple of the wheel
    positions (as letters)"""
    def __getattribute__(self, name):
        if name=='wheel_positions':
            return self.wheel1.position, self.wheel2.position, self.wheel3.position 
        elif name=='wheel_positions_l':
            return self.wheel1.position_l, self.wheel2.position_l, self.wheel3.position_l 
        else:
            return object.__getattribute__(self, name)
    
    def advance(self, wheel1=False, wheel2=False, wheel3=True):
        """Advance some wheels of a scrambler.
        """
        if wheel1: self.wheel1.advance()
        if wheel2: self.wheel2.advance()
        if wheel3: self.wheel3.advance()
            
    def lookup(self, letter):
        """Lookup the decipherment of a letter, given a particular scrambler
        orientation.
        """
        a = self.wheel3.forward(letter)
        b = self.wheel2.forward(a)
        c = self.wheel1.forward(b)
        d = self.reflector.forward(c)
        e = self.wheel1.backward(d)
        f = self.wheel2.backward(e)
        g = self.wheel3.backward(f)
        return g
    
    def set_positions(self, wheel1_pos, wheel2_pos, wheel3_pos):
        """Set the positions of a scrambler's wheels.
        """
        self.wheel1.set_position(wheel1_pos)
        self.wheel2.set_position(wheel2_pos)
        self.wheel3.set_position(wheel3_pos)        


class Bombe(object):
    """An entire Bombe machine.

    This specifies the pattern of the wheels and reflectors used. The 
    scramblers are connected and wired up according the to the specification
    given by the menu. 

    Bombe objects are callable. Calling a Bombe (with the starting scrambler 
    positions) calls the `test` method and  returns the pair of 
    `start_positions` and the result of `test`.

    Bombe objects have attributes `wheel_positions` and `wheel_positions_l`, 
    which return the results of the scramblers' `Scrambler.wheel_positions` 
    and `Scrambler.wheel_positions_l`.
    """
    
    def __init__(self, wheel1_spec, wheel2_spec, wheel3_spec, reflector_spec,
                menu=None, start_signal=None, use_diagonal_board=True, 
                verify_plugboard=True):
        self.connections = []
        self.wheel1_spec = wheel1_spec
        self.wheel2_spec = wheel2_spec
        self.wheel3_spec = wheel3_spec
        self.reflector_spec = reflector_spec
        if menu:
            self.read_menu(menu)
        if start_signal:
            self.test_start = start_signal
        self.use_diagonal_board = use_diagonal_board
        self.verify_plugboard = verify_plugboard
        
    __pdoc__['Bombe.wheel_positions'] = """Return a 3-tuple of the wheel
    positions (as numbers)"""
    __pdoc__['Bomb3.wheel_positions_l'] = """Return a 3-tuple of the wheel
    positions (as letters)"""
    def __getattribute__(self, name):
        if name=='wheel_positions':
            return self.connections[0].scrambler.wheel_positions
        elif name=='wheel_positions_l':
            return self.connections[0].scrambler.wheel_positions_l
        else:
            return object.__getattribute__(self, name)
        
    def __call__(self, start_positions):
        return start_positions, self.test(initial_signal=self.test_start,
            start_positions=start_positions, 
            use_diagonal_board=self.use_diagonal_board,
            verify_plugboard=self.verify_plugboard)
        
    def add_connection(self, bank_before, bank_after, scrambler):
        """Create a new connection between banks.
        """
        self.connections += [Connection([bank_before, bank_after], scrambler)]
        
    def read_menu(self, menu):
        """Read a menu, creating one scrambler for each element of the menu 
        and setting up the connections it implies. Also defines the most 
        common letter in the menu's plaintext as the default letter to start 
        testing with."""
        self.connections = []
        for item in menu:
            scrambler = Scrambler(self.wheel1_spec, self.wheel2_spec, self.wheel3_spec,
                                  self.reflector_spec,
                                  wheel3_pos=unpos(item.number - 1))
            self.add_connection(item.before, item.after, scrambler)
        most_common_letter = (collections.Counter(m.before for m in menu) +\
            collections.Counter(m.after for m in menu)).most_common(1)[0][0]
        self.test_start = Signal(most_common_letter, most_common_letter)
        
    def set_positions(self, wheel1_pos, wheel2_pos, wheel3_pos):
        """Set positions of all scramblers. The first scrambler will be set
        to the specified positions. The second scrambler will have its
        third wheel advanced one position; the third scramber will have its
        third wheel advanced two positios; and so on. Not that the first and
        second wheels of the scramblers are never advanced in setup."""
        for i, c in enumerate(self.connections):
            c.scrambler.set_positions(wheel1_pos, wheel2_pos, unpos(pos(wheel3_pos) + i))
    
    def test(self, initial_signal=None, start_positions=None, use_diagonal_board=True,
            verify_plugboard=True):
        """Test a scrambler setting. It creates a signal (held in 
        `self.pending`) on the `initial_signal` wire then uses 
        `Bombe.propagate` to propagate the signal across the Bombe. 

        Returns a Boolean recording if this scrambler setting with
        this signal is a "stop" (potential valid scrambler setting).

        * If `initial_signal` is `None`, use the default starting signal set in
          `Bombe.read_menu`
        * If `start_positions` is `None`, use the existing scramber positions."""
        self.banks = {label: 
                      dict(zip(string.ascii_lowercase, 
                        [False]*len(string.ascii_lowercase)))
                      for label in string.ascii_lowercase}
        if start_positions:
            self.set_positions(*start_positions)
        if not initial_signal:
            initial_signal = self.test_start
        self.pending = [initial_signal]
        self.propagate(use_diagonal_board)
        live_wire_count = len([self.banks[self.test_start.bank][w] 
                    for w in self.banks[self.test_start.bank] 
                    if self.banks[self.test_start.bank][w]])
        if live_wire_count < 26:
            if verify_plugboard:
                possibles = self.possible_plugboards()
                return all(s0.isdisjoint(s1) 
                           for s0 in possibles 
                           for s1 in possibles 
                           if s0 != s1)
            else:
                return True
        else:
            return False
        
    def propagate(self, use_diagonal_board):
        """Propagate a signal through the Bombe. Uses `self.pending` as an 
        agenda for a breadth-first search. Each element on the agenda represents 
        a particular wire in a bank that is being "energised" (set to `True`).
        The first element in the agenda is removed, the wire/bank is set, 
        then all connected wire/banks are added to the `self.pending`
        agenda.
        """
        while self.pending:
            current = self.pending[0]
            # print("processing", current)
            self.pending = self.pending[1:]
            if not self.banks[current.bank][current.wire]:
                self.banks[current.bank][current.wire] = True
                if use_diagonal_board:
                    self.pending += [Signal(current.wire, current.bank)]
                for c in self.connections:
                    if current.bank in c.banks:
                        other_bank = [b for b in c.banks if b != current.bank][0]
                        other_wire = c.scrambler.lookup(current.wire)
                        # print("  adding", other_bank, other_wire, "because", c.banks)
                        self.pending += [Signal(other_bank, other_wire)]
    
    def run(self, run_start=None, wheel1_pos='a', wheel2_pos='a', wheel3_pos='a', 
        use_diagonal_board=True):
        """Run a Bombe after setup with a menu, by trying all scramber 
        positions. For each scrambler position, `Bombe.test` is run. If the 
        test is successful, the scrambler positiions are added to `self.solutions`.
        `self.Solutions` is returned.
        """
        if not run_start:
            run_start = self.test_start
        self.solutions = []
        self.set_positions(wheel1_pos, wheel2_pos, wheel3_pos)
        for run_index in range(26*26*26):
            if self.test(initial_signal=run_start, use_diagonal_board=use_diagonal_board):
                self.solutions += [self.connections[0].scrambler.wheel_positions_l]
            advance3 = True
            advance2 = False
            advance1 = False
            if (run_index + 1) % 26 == 0: advance2 = True
            if (run_index + 1) % (26*26) == 0: advance1 = True
            for c in self.connections:
                c.scrambler.advance(advance1, advance2, advance3)
        return self.solutions
    
    def possible_plugboards(self):
        """Given a Bombe after a `Bombe.test` has been performed, determine
        what plugboard settings can be derived from the solution.
        """
        possibles = set()
        for b in self.banks:
            active = [w for w in self.banks[b] if self.banks[b][w]]
            inactive = [w for w in self.banks[b] if not self.banks[b][w]]
            if len(active) == 1:
                possibles = possibles.union({frozenset((b, active[0]))})
            if len(inactive) == 1:
                possibles = possibles.union({frozenset((b, inactive[0]))})
        return possibles


def run_multi_bombe(wheel1_spec, wheel2_spec, wheel3_spec, reflector_spec, menu,
                    start_signal=None, use_diagonal_board=True, 
                    verify_plugboard=True):
    """Run a Bombe solution, spreading the load across multiple CPU cores.
    Similar to `Bombe.run` in effects, but quicker on a multi-core machine.
    """
    allwheels = itertools.product(string.ascii_lowercase, repeat=3)

    with multiprocessing.Pool() as pool:
        res = pool.map(Bombe(wheel1_spec, wheel2_spec, wheel3_spec, 
            reflector_spec, menu=menu, start_signal=start_signal, 
            use_diagonal_board=use_diagonal_board, 
            verify_plugboard=verify_plugboard),
                  allwheels)
    return [r[0] for r in res if r[1]]