
# TODO:
# - algo afmaken, vergelijken met mascot: http://www.matrixscience.com/training/pmf1_q.html
# - denk na?
# - schrijf iets op...

import sys
import math
import random
import heapq

from Bio import SeqIO

amino_weights = {
    "A": 71.037,
    "R": 156.101,
    "N": 114.043,
    "D": 115.027,
    "C": 103.009,
    "E": 129.043,
    "Q": 128.059,
    "G": 57.021,
    "H": 137.059,
    "I": 113.084,
    "L": 113.084,
    "K": 128.095,
    "M": 131.040,
    "F": 147.068,
    "P": 97.053,
    "S": 87.032,
    "T": 101.048,
    "W": 186.079,
    "Y": 163.063,
    "V": 99.068,
    "U": 0
}

water = 18.011
proton = 1.007

def trypsine(seq):
    buf = ""
    chunks = []

    for i in range(len(seq)-1):
        buf += seq[i]
        if (seq[i] == "R" or seq[i] == "K") and not (seq[i+1] == "P"):
            if buf != "":
                chunks.append(buf)
                buf = ""
    
    buf += seq[-1]
    chunks.append(buf)
    
    return chunks


def peptide_weight(seq):
    return sum(amino_weights[c] for c in seq) + water + proton


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


def load_sample(fname):
    with open(fname) as f:
        return sorted(float(l.strip()) for l in f.readlines() if not l.isspace())


class ProteinDB:
    def __init__(self, fname):
        self.proteins = list(SeqIO.parse(fname, "fasta"))
        
        for prot in self.proteins:
            prot.chunks = trypsine(prot.seq)
            prot.weights = sorted(set(peptide_weight(c) for c in prot.chunks))
    
    def find_best_matches(self, sample, amount=10):
        scored = [(p, score(sample, p.weights)) for p in self.proteins]
        return heapq.nlargest(amount, scored, key=lambda t: t[1])


if __name__ == "__main__":
    sample = load_sample("PMF1.txt")
    db = ProteinDB("uniprot_sprot_human.fasta")
    scores = db.find_best_matches(sample)
    for r, score in scores:
        print("{: <30} {}".format(r.id, score))

