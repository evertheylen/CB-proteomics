
from Bio import SeqIO

from .etc import *
from .io import *
from .MS1 import ProteinDB


def create_ion(_extra_mass, reverse):
    '''Creates functions that return the masses of the fragments after
    MS2 fragmentation by some ion.'''
    
    if reverse:
        def ion(seq, extra_mass=_extra_mass):
            return [sum(amino_weights[c] for c in seq[i:]) + extra_mass
                    for i in range(len(s)-1, -1, -1)]
    else:
        def ion(seq, extra_mass=_extra_mass):
            return [sum(amino_weights[c] for c in seq[:i]) + extra_mass
                    for i in range(1, len(s)+1)]
    return ion

y_ion = create_ion(water + proton, True)
b_ion = create_ion(proton, False)


class ProteinDB2(ProteinDB):
    def __init__(self, fname=data_loc('uniprot-human-reviewed-trypsin-november-2016.fasta'), 
                 missed_cleavages=1, ion=y_ion):
        super().__init__(fname, missed_cleavages=missed_cleavages)
        # We already know the peptides, now we have to cut it up once more
        self.tandem = []  # list of (prot, peptide, list of fragment weights)
        for prot in self.proteins:
            for peptide in prot.chunks:
                self.tandem.append((prot, peptide, ion(peptide)))
    
    def find_best_proteins(self, sample, amount=10):
        if isinstance(sample, list):
            super().find_best_proteins(sample, amount)
        else:
            raise NotImplemented("So far, protein inference isn't implemented")
    
    def find_best_peptides(self, sample, amount=10):
        
        
        

if __name__ == '__main__':
    print('Work in progress!')
