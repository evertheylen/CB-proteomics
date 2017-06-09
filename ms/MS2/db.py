"""Contains the MS2 database and some ionization code
"""

import heapq
from itertools import chain

from ms.util import *
from ms.MS1 import ProteinDB
from .spectra import *


def create_ion(_extra_mass, reverse):
    '''Creates a function that returns the masses of the fragments 
    after MS2 fragmentation by some type of ion.'''
    
    if reverse:
        def ion(seq, extra_mass=_extra_mass):
            return [sum(amino_weights[c] for c in seq[i:]) + extra_mass
                    for i in range(len(seq)-1, -1, -1)]
    else:
        def ion(seq, extra_mass=_extra_mass):
            return [sum(amino_weights[c] for c in seq[:i]) + extra_mass
                    for i in range(1, len(seq)+1)]
    return ion


y_ion = create_ion(water + proton, True)
b_ion = create_ion(proton, False)


class Ionizer:
    # In the future, more ionizers can be added
    def __init__(self, ions=(b_ion, y_ion)):
        self.ions = ions
    
    def __call__(self, seq):
        return sum((ion(seq) for ion in self.ions), [])
    
# Ionizer can't be pickled, so for now we just use a default one
Ionizer.default = Ionizer()


class ProteinDB2(Pickled):
    #default_file = data_loc('uniprot-human-reviewed-trypsin-november-2016-small.fasta')
    default_file = data_loc('uniprot-human-reviewed-trypsin-november-2016.fasta')
    
    def __init__(self, fname=None, missed_cleavages=1, pep_tolerance=1.2):
        fname = fname or self.default_file
        self.pep_tolerance = pep_tolerance
        
        # So far we don't do extensive analysis on the level of peptides.
        # Specifically, no analysis of the target/decoy kind is done. 
        # For simplicity, we leave peptides as simple strings and store
        # the target/decoy info in sets (which are blazingly fast anyway)
        target_prot = ProteinDB(fname, missed_cleavages)
        self.targets = set(target_prot.get_peptides())
        decoy_prot = ProteinDB(fname, missed_cleavages, reverse=True)
        self.decoys = set(decoy_prot.get_peptides())
        print(progress_start.format('Forming peptide list'), end='')
        self.peptides = SortedCollection(self.targets | self.decoys, key=peptide_mass)
        print(progress_end.format('Forming peptide list'))
    
    def find_best_proteins(self, sample: list, amount=10):
        raise NotImplemented("Protein inference isn't implemented")
    
    def peptide_scores(self, espec, scorer) -> '[(name, score)]':
        espec = scorer.preprocess_espec(espec)
        
        # First, filter on peptide mass
        candidate_peptides = self.peptides.find_between(espec.pepmass - self.pep_tolerance,
                                                        espec.pepmass + self.pep_tolerance)
        
        # Then, determine tandem scores
        for pep in candidate_peptides:
            tag = 'TARGET' if pep in self.targets else 'DECOY '
            tspec = TheoMs2Spectrum(title = tag + ' ' + pep,
                                    pepmass = peptide_mass(pep),
                                    peaks = Ionizer.default(pep))
            yield (tspec.title, scorer.score(tspec, espec))
    
    def find_best_peptides(self, tspec, scorer, amount=10):
        return heapq.nlargest(amount, self.peptide_scores(tspec, scorer), key=lambda t: t[1])

