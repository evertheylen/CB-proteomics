
import math
import random
import heapq

from Bio import SeqIO

from .etc import *
from .util import *


def load_peaks(fname):
    with open(fname) as f:
        return sorted(float(l) for l in nice_lines(f))


def shared_peak(sample, weights, tolerance=1.2):
    i = 0
    j = 0
    score = 0
    while i != len(sample) and j != len(weights):
        if abs(sample[i] - weights[j]) <= tolerance:
            score += 1
        
        if (sample[i] < weights[j] and not i == len(weights)-1) or j == len(weights)-1:
            i += 1
        else:
            j += 1
    
    return score

def relative_shared_peak(sample, weights, tolerance=1.2):
    return shared_peak(sample, weights, tolerance)/len(weights)

class ProteinDB:
    default_file = data_loc('uniprot_sprot_human.fasta')
    
    def __init__(self, fname=None, missed_cleavages=0):
        fname = fname or self.default_file
        self.proteins = list(SeqIO.parse(fname, 'fasta'))
        for prot in progress_bar(self.proteins, 'Loading proteins'):
            prot.chunks = trypsine(prot.seq, missed_cleavages)
            prot.weights = sorted(set(peptide_weight(c) for c in prot.chunks))
    
    def find_best_proteins(self, sample, amount=10):
        scored = [(p, relative_shared_peak(sample, p.weights)) for p in self.proteins]
        return heapq.nlargest(amount, scored, key=lambda t: t[1])


if __name__ == '__main__':
    import sys
    sample = load_peaks(sys.argv[1])
    db = ProteinDB()
    print_scores(db.find_best_proteins(sample), lambda r: r.id)



# Tests

import unittest

class MS1Test(unittest.TestCase):
    @unittest.skip('Skipping long test')
    def test_HYEP(self):
        db = ProteinDB()
        sample = load_peaks(data_loc('PMF1.txt'))
        (r, score), = db.find_best_proteins(sample, 1)
        self.assertEqual(r.id, 'sp|P07099|HYEP_HUMAN')
        self.assertAlmostEqual(score, 0.29545454545454547)

