
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

def trypsine(seq, missed_cleavages=0):
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
    
    mc_chunks = []
    for length in range(1, missed_cleavages+1):
        for i in range(len(chunks)-length):
            mc_chunks.append(''.join(chunks[i:i+length+1]))
    
    return chunks + mc_chunks


def peptide_weight(seq):
    return sum(amino_weights[c] for c in seq) + water + proton



# Tests

import unittest

class Trypsine(unittest.TestCase):
    def test_basic(self):
        chunks = trypsine('GARFIELDDEKARPER')
        self.assertEqual(chunks, ['GAR', 'FIELDDEK', 'ARPER'])
    
    def test_1_missed_cleavages(self):
        chunks = trypsine('GARFIELDDEKARPER', 1)
        self.assertEqual(chunks, ['GAR', 'FIELDDEK', 'ARPER',
                                  'GARFIELDDEK', 'FIELDDEKARPER'])
    
    def test_2_missed_cleavages(self):
        chunks = trypsine('GARFIELDDEKARPER', 2)
        self.assertEqual(chunks, ['GAR', 'FIELDDEK', 'ARPER',
                                  'GARFIELDDEK', 'FIELDDEKARPER',
                                  'GARFIELDDEKARPER'])

