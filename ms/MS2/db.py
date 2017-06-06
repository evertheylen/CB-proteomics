"""Contains the MS2 database and some ionization code
"""

import heapq

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


class ProteinDB2(Pickled):
    #default_file = data_loc('uniprot-human-reviewed-trypsin-november-2016.fasta')
    default_file = data_loc('uniprot-human-reviewed-trypsin-november-2016-small.fasta')
    
    def __init__(self, fname = None, missed_cleavages=1, ionizer=Ionizer()):
        fname = fname or self.default_file
        self.targets = ProteinDB(fname, missed_cleavages).proteins
        self.decoys = ProteinDB(fname, missed_cleavages, reverse=True).proteins
        # We already know the peptides, now we have to cut it up once more
        self.tandem = {}
        self._process_proteins(self.targets, 'TARGET', ionizer)
        self._process_proteins(self.decoys, 'DECOY ', ionizer)
    
    def _process_proteins(self, proteins, tag, ionizer):
        for prot in progress_bar(proteins, 'Splitting in ions, tagged `{}`'.format(tag)):
            for peptide in prot.chunks:
                if peptide not in self.tandem:
                    self.tandem[peptide] = TheoMs2Spectrum(title = tag + ' ' + peptide,
                                                           pepmass = peptide_weight(peptide),
                                                           peaks = ionizer(peptide))
    
    def find_best_proteins(self, sample: list, amount=10):
        raise NotImplemented("Protein inference isn't implemented")
    
    def peptides_scores(self, sample: list, scorer) -> '[(name, score)]':
        if hasattr(scorer, 'preprocess_espec'):
            sample = [scorer.preprocess_espec(sample) for espec in progress_bar(sample, "Preprocessing sample")]
        
        for pep, tspec in progress_bar(self.tandem.items(), "Scoring peptides"):
            for espec in sample:
                yield (tspec.title, scorer.score(tspec, espec))
    
    def find_best_peptides(self, sample: list, scorer, amount=10):
        return heapq.nlargest(amount, self.peptides_scores(sample, scorer), key=lambda t: t[1])
