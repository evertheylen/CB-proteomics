
import heapq
from itertools import repeat, chain

from .etc import *
from .util import *
from .MS1 import ProteinDB, shared_peak


def weighted_shared_peaks(sample, weights, tolerance=1.2):
    i = 0
    j = 0
    score = 0
    while i != len(sample) and j != len(weights):
        if abs(sample[i][0] - weights[j]) <= tolerance:
            score += 1 #sample[i][1]
        
        if (sample[i][0] < weights[j] and not i == len(weights)-1) or j == len(weights)-1:
            i += 1
        else:
            j += 1
    
    return score

class MS2Spectrum:
    def __init__(self, title, pepmass, peaks, **kwargs):
        self.title = title
        self.pepmass = pepmass
        self.peaks = sorted(peaks, key=lambda t: t[0])
    
    @staticmethod
    def key_value(line):
        parts = line.strip().split('=', 1)
        if len(parts) < 2:
            return None
        return parts[0].strip().upper(), parts[1].strip()
    
    @classmethod
    @simple_progress('Loading MS2 spectra')
    def load_spectra(cls, fname, maximum=float('inf')):
        spectra = []
        with open(fname) as f:
            lines = nice_lines(f)
            for line in lines:
                if line == 'BEGIN IONS':
                    peaks = []
                    metadata = {}
                    
                    for peak in lines:
                        if peak == 'END IONS': 
                            break
                        kv = cls.key_value(peak)
                        if kv:
                            metadata[kv[0]] = kv[1]
                        else:
                            location, intensity = peak.split()
                            peaks.append((float(location.strip()), float(intensity.strip())))
                            #peaks.append(float(location.strip()))
                    
                    spectra.append(cls(metadata.pop('TITLE'), metadata.pop('PEPMASS'),
                                       peaks, **metadata))
                    if len(spectra) >= maximum:
                        break
        return spectra



def create_ion(_extra_mass, reverse):
    '''Creates a function that returns the masses of the fragments after
    MS2 fragmentation by some ion.'''
    
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
    default_file = data_loc('uniprot-human-reviewed-trypsin-november-2016.fasta')
    
    def __init__(self, fname = None, missed_cleavages=1, ionizer=Ionizer()):
        fname = fname or self.default_file
        self.targets = ProteinDB(fname, missed_cleavages).proteins
        self.decoys = ProteinDB(fname, missed_cleavages, reverse=True).proteins
        # We already know the peptides, now we have to cut it up once more
        self.tandem = {}
        #self.tandem_inference = multimap()
        for target, prot in progress_bar(self.marked_proteins(), 'Splitting in ions'):
            for peptide in prot.chunks:
                if peptide not in self.tandem:
                    self.tandem[peptide] = (target, ionizer(peptide))
                    #self.tandem_inference[peptide].add(prot)
    
    @generator_length(lambda self: len(self.targets) + len(self.decoys))
    def marked_proteins(self):
        yield from zip(repeat(True), self.targets)
        yield from zip(repeat(False), self.decoys)
    
    def find_best_proteins(self, sample: list, amount=10):
        raise NotImplemented("Protein inference isn't implemented")
    
    def peptides_scores(self, sample, tolerance, title="Calculating scores"):
        for pep, (target, weights) in progress_bar(self.tandem.items(), title):
            for spec in sample:
                yield (('TARGET' if target else 'DECOY ') + ' ' + pep, 
                       weighted_shared_peaks(spec.peaks, weights, tolerance))
    
    def find_best_peptides(self, sample: list, amount=10, tolerance=0.6):
        return heapq.nlargest(amount, self.peptides_scores(sample, tolerance), key=lambda t: t[1])



if __name__ == '__main__':
    db_loc = 'ms2.db'
    import sys
    sample = MS2Spectrum.load_spectra(sys.argv[1], 2)
    try:
        db = ProteinDB2.load(db_loc)
        save = False
    except Exception as e:
        print("Couldn't load ms2.db ({}), creating a new one".format(e))
        save = True
        db = ProteinDB2()
    
    try:
        print_scores(db.find_best_peptides(sample))
    except Exception as e:
        if save:
            db.save(db_loc)
        raise e
    
    if save:
        db.save(db_loc)

