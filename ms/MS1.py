
import sys
import math
import random
import heapq

from Bio import SeqIO

from .etc import *
from .io import *


def load_sample(fname):
    with open(fname) as f:
        return sorted(float(l.strip()) for l in f.readlines() if not l.isspace())


def score(sample, weights, tolerance=1.2):
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
    
    return score/len(weights)


class ProteinDB:
    def __init__(self, fname=data_loc('uniprot_sprot_human.fasta'), missed_cleavages=0):
        self.proteins = list(SeqIO.parse(fname, 'fasta'))
        
        for prot in self.proteins:
            prot.chunks = trypsine(prot.seq, missed_cleavages)
            prot.weights = sorted(set(peptide_weight(c) for c in prot.chunks))
    
    def find_best_proteins(self, sample, amount=10):
        scored = [(p, score(sample, p.weights)) for p in self.proteins]
        return heapq.nlargest(amount, scored, key=lambda t: t[1])


if __name__ == '__main__':
    sample = load_sample(sys.argv[1])
    db = ProteinDB()
    scores = db.find_best_proteins(sample)
    for r, score in scores:
        print('{: <30} {}'.format(r.id, score))



# Tests

import unittest

class MS1Test(unittest.TestCase):
    @unittest.skip('Skipping long test')
    def test_HYEP(self):
        db = ProteinDB()
        sample = load_sample(data_loc('PMF1.txt'))
        (r, score), = self.db.find_best_matches(sample, 1)
        self.assertEqual(r.id, 'sp|P07099|HYEP_HUMAN')
        self.assertAlmostEqual(score, 0.29545454545454547)

