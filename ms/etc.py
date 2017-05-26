
from .util import memoize

amino_weights = {
    'A': 71.037,
    'R': 156.101,
    'N': 114.043,
    'D': 115.027,
    'C': 103.009,
    'E': 129.043,
    'Q': 128.059,
    'G': 57.021,
    'H': 137.059,
    'I': 113.084,
    'L': 113.084,
    'K': 128.095,
    'M': 131.040,
    'F': 147.068,
    'P': 97.053,
    'S': 87.032,
    'T': 101.048,
    'W': 186.079,
    'Y': 163.063,
    'V': 99.068,
    'U': 0
}

water = 18.011
proton = 1.007

class _trypsine:
    def __init__(self, missed_cleavages=0):
        self.missed_cleavages = missed_cleavages
    
    def __call__(self, seq):
        'Cleaves after K or R unless they are followed by P'
        buf = ''
        chunks = []
        
        for i in range(len(seq)-1):
            buf += seq[i]
            if (seq[i] == 'R' or seq[i] == 'K') and not (seq[i+1] == 'P'):
                chunks.append(buf)
                buf = ''
        
        buf += seq[-1]
        chunks.append(buf)
        yield from chunks
        
        for length in range(1, self.missed_cleavages+1):
            for i in range(len(chunks)-length):
                yield ''.join(chunks[i:i+length+1])

@memoize
def trypsine(missed_cleavages=0):
    return _trypsine(missed_cleavages)

def peptide_weight(seq):
    return sum(amino_weights[c] for c in seq) + water + proton



# Replaced the BioPython dependency with this, so no libraries are used.
# This means we can use PyPy and (hopefully) gain a considerable speedup.

class Sequence:
    def __init__(self, name, seq, weights=None, chunker=lambda s: [s]):
        self.name = name
        self.seq = seq
        self.weights = weights
        self.chunker = chunker
    
    @property
    def chunks(self):
        yield from self.chunker(self.seq)
    
    __slots__ = ('name', 'seq', 'chunker', 'weights')
    

def read_fasta(filename):
    sequences = []
    buf = ""
    name = ""
    with open(filename) as f:
        for l in f.readlines():
            if len(l) > 0:
                if l[0] == ">":
                    if buf != "":
                        sequences.append(Sequence(name.strip(), buf))
                        buf = ""
                    name = l[1:]
                else:
                    buf += l[:-1]
    if buf != "":
        sequences.append(Sequence(name.strip(), buf))
    return sequences


# Tests

import unittest

class Trypsine(unittest.TestCase):
    def test_basic(self):
        chunks = list(trypsine('GARFIELDDEKARPER'))
        self.assertEqual(chunks, ['GAR', 'FIELDDEK', 'ARPER'])
    
    def test_1_missed_cleavages(self):
        chunks = list(trypsine('GARFIELDDEKARPER', 1))
        self.assertEqual(chunks, ['GAR', 'FIELDDEK', 'ARPER',
                                  'GARFIELDDEK', 'FIELDDEKARPER'])
    
    def test_2_missed_cleavages(self):
        chunks = list(trypsine('GARFIELDDEKARPER', 2))
        self.assertEqual(chunks, ['GAR', 'FIELDDEK', 'ARPER',
                                  'GARFIELDDEK', 'FIELDDEKARPER',
                                  'GARFIELDDEKARPER'])

