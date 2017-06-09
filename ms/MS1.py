"""MS1 implementation. Unlike MS2, it's simple enough to be contained in a single file.
Also includes a commandline interface.
"""

import math
import random
import heapq

from ms.util import *


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


class ProteinDB(Pickled):
    default_file = data_loc('uniprot_sprot_human.fasta')
    
    def __init__(self, fname=None, missed_cleavages=0, reverse=False):
        fname = fname or self.default_file
        self.proteins = list(map((reversed if reverse else identity), read_fasta(fname)))
        
        chunker = trypsine(missed_cleavages)
        for prot in progress_bar(self.proteins, 'Loading proteins' + (' in reverse' if reverse else '')):
            prot.chunks = list(chunker(prot.seq))
            prot.weights = sorted(set(peptide_mass(c) for c in prot.chunks))
    
    def find_best_proteins(self, sample, amount=10, tolerance=1.2):
        if isinstance(sample, str):
            sample = load_peaks(sample)
        scored = ((p, relative_shared_peak(sample, p.weights, tolerance))
                  for p in progress_bar(self.proteins, 'Scoring proteins'))
        return heapq.nlargest(amount, scored, key=lambda t: t[1])
    
    def get_peptides(self):
        for prot in progress_bar(self.proteins, 'Loading peptides'):
            yield from prot.chunks


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='MS2 database search')
    parser.add_argument('-d', '--database', help='FASTA file to use for the database', 
                                            default=ProteinDB.default_file)
    parser.add_argument('-a', '--amount', help='Amount of results', type=int, default=10)
    parser.add_argument('-t', '--tolerance', help='Tolerance', type=float, default=1.2)
    parser.add_argument('sample', help='PMF file')
    args = parser.parse_args()
    sample = load_peaks(args.sample)
    db = ProteinDB(args.database)
    print_scores(db.find_best_proteins(sample, args), lambda r: r.name[:70],
                 amount=args.amount, tolerance=args.tolerance)



# Tests

import unittest

class MS1Test(unittest.TestCase):
    @unittest.skip('Skipping long test')
    def test_HYEP(self):
        db = ProteinDB()
        sample = load_peaks(data_loc('PMF1.txt'))
        (r, score), = db.find_best_proteins(sample, 1)
        self.assertIn('sp|P07099|HYEP_HUMAN', r.name)
        self.assertAlmostEqual(score, 0.29545454545454547)

