import pytest
import string 

from szyfrow.enigma import *
from szyfrow.bombe import *

@pytest.fixture
def sample_scrambler():
    return Scrambler(wheel_i_spec, wheel_ii_spec, 
        wheel_iii_spec, reflector_b_spec)

def test_attributes(sample_scrambler):
    assert sample_scrambler.wheel_positions == (0, 0, 0)
    assert sample_scrambler.wheel_positions_l == ('a', 'a', 'a')

def test_set_positions(sample_scrambler):
    sample_scrambler.set_positions(1, 2, 3)
    assert sample_scrambler.wheel_positions == (1, 2, 3)
    assert sample_scrambler.wheel_positions_l == ('b', 'c', 'd')
    sample_scrambler.set_positions('p', 'q', 'r')
    assert sample_scrambler.wheel_positions == (15, 16, 17)
    assert sample_scrambler.wheel_positions_l == ('p', 'q', 'r')

def test_advance(sample_scrambler):
    assert sample_scrambler.wheel_positions == (0, 0, 0)
    sample_scrambler.advance()
    assert sample_scrambler.wheel_positions == (0, 0, 1)
    sample_scrambler.advance()
    assert sample_scrambler.wheel_positions == (0, 0, 2)
    sample_scrambler.set_positions(0, 0, 25)
    assert sample_scrambler.wheel_positions == (0, 0, 25)
    sample_scrambler.advance()
    assert sample_scrambler.wheel_positions == (0, 0, 0)
    sample_scrambler.set_positions(0, 0, 25)
    sample_scrambler.advance(wheel3=False)
    assert sample_scrambler.wheel_positions == (0, 0, 25)
    sample_scrambler.set_positions(0, 0, 25)
    sample_scrambler.advance(wheel2=True)
    assert sample_scrambler.wheel_positions == (0, 1, 0)
    sample_scrambler.set_positions(0, 0, 25)
    sample_scrambler.advance(wheel1=True, wheel2=True)
    assert sample_scrambler.wheel_positions == (1, 1, 0)

def test_lookups(sample_scrambler):
    sample_scrambler.set_positions(0, 0, 0)
    lookups = cat(sample_scrambler.lookup(l) for l in string.ascii_lowercase)
    assert lookups == 'uejobtpzwcnsrkdgvmlfaqiyxh'
    lookups = cat(sample_scrambler.lookup(l) for l in 'uejobtpzwcnsrkdgvmlfaqiyxh')
    assert lookups == 'abcdefghijklmnopqrstuvwxyz'
    sample_scrambler.set_positions('p', 'q', 'r')
    lookups =  cat(sample_scrambler.lookup(l) for l in string.ascii_lowercase)
    assert lookups == 'jgqmnwbtvaurdezxclyhkifpso'
    lookups = cat(sample_scrambler.lookup(l) for l in 'jgqmnwbtvaurdezxclyhkifpso')
    assert lookups == 'abcdefghijklmnopqrstuvwxyz'


@pytest.fixture
def sample_bombe():
    bombe = Bombe(wheel_i_spec, wheel_ii_spec, wheel_iii_spec, reflector_b_spec)
    plaintext = 'thisisatestmessage'
    ciphertext = 'opgndxcrwomnlnecjz'
    menu = make_menu(plaintext, ciphertext)
    bombe.read_menu(menu)
    return bombe

def test_menu(sample_bombe):
    assert len(sample_bombe.connections) == 18
    banks = ':'.join(sorted(cat(sorted(c.banks))
            for c in sample_bombe.connections))
    assert banks == 'ac:ac:di:el:es:ew:ez:gi:gj:hp:mn:mt:ns:ns:os:ot:rt:sx'
    wheel_pos = ':'.join(sorted(cat(c.scrambler.wheel_positions_l)
            for c in sample_bombe.connections))
    assert wheel_pos == 'aaa:aab:aac:aad:aae:aaf:aag:aah:aai:aaj:aak:aal:aam:aan:aao:aap:aaq:aar'

    assert len(sample_bombe.connections) == 18

def test_signal(sample_bombe):
    sample_bombe.test(Signal('t', 't'))
    assert len(sample_bombe.banks['t']) == 26
    assert all(sample_bombe.banks['t'].values()) == True
    assert sum(1 for s in sample_bombe.banks['u'].values() if s) == 18

    sample_bombe.set_positions('a', 'a', 'b')
    sample_bombe.test()
    n_active_banks = sum(1 for b in sample_bombe.banks 
            for s in sample_bombe.banks[b].values() if s)
    assert n_active_banks == 11

def test_valid_with_rings():
    pt31 = 'someplaintext'
    ct31 = 'dhnpforeeimgg'
    menu31 = make_menu(pt31, ct31)
    b31 = Bombe(wheel_i_spec, wheel_v_spec, wheel_iii_spec, reflector_b_spec)
    b31.read_menu(menu31)
    b31.set_positions('e', 'l', 'f')

    b31.test(Signal('s', 'o'))
    n_active_banks = sum(1 for b in b31.banks 
            for s in b31.banks[b].values() if s)
    plugboards = ':'.join(sorted(cat(sorted(p)) 
            for p in b31.possible_plugboards()))
    assert n_active_banks == 5
    assert plugboards == 'd:hl:os'

    b31.test(Signal('o', 'o'))
    n_active_banks = sum(1 for b in b31.banks 
            for s in b31.banks[b].values() if s)
    plugboards = ':'.join(sorted(cat(sorted(p)) 
            for p in b31.possible_plugboards()))
    assert n_active_banks == 507
    assert plugboards == 'bg:ey:fp:in:m:tx'

def test_invalid_with_rings():
    pt31 = 'someplaintext'
    ct31 = 'dhnpforeeimgg'
    menu31 = make_menu(pt31, ct31)
    b31 = Bombe(wheel_i_spec, wheel_v_spec, wheel_iii_spec, reflector_b_spec)
    b31.read_menu(menu31)
    b31.set_positions('a', 'a', 'a')

    b31.test(Signal('a', 'o'))
    n_active_banks = sum(1 for b in b31.banks 
            for s in b31.banks[b].values() if s)
    plugboards = ':'.join(sorted(cat(sorted(p)) 
            for p in b31.possible_plugboards()))
    assert n_active_banks == 514
    assert plugboards == ''

