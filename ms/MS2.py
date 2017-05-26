
import heapq

from .etc import *
from .util import *
from .MS1 import ProteinDB, shared_peak


class MS2Spectrum:
    def __init__(self, title, pepmass, peaks, **kwargs):
        self.title = title
        self.pepmass = pepmass
        self.peaks = sorted(peaks)  #, key=lambda t: t[0])
    
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
                            #peaks.append((float(location.strip()), float(intensity.strip())))
                            peaks.append(float(location.strip()))
                    
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


class ProteinDB2(Pickled):
    default_file = data_loc('uniprot-human-reviewed-trypsin-november-2016.fasta')
    
    def __init__(self, fname = None, missed_cleavages=1, ion=y_ion):
        fname = fname or self.default_file
        self.db1 = ProteinDB(fname, missed_cleavages)
        self.proteins = self.db1.proteins
        # We already know the peptides, now we have to cut it up once more
        self.tandem = {}
        #self.tandem_inference = multimap()
        for prot in progress_bar(self.proteins, 'Splitting in ions'):
            for peptide in prot.chunks:
                if peptide not in self.tandem:
                    #continue
                    self.tandem[peptide] = ion(peptide)
                    #self.tandem_inference[peptide].add(prot)
    
    def find_best_proteins(self, sample: list, amount=10):
        raise NotImplemented("Protein inference isn't implemented")
    
    def find_best_peptides(self, sample: list, amount=10, minlen=20):
        scores = []
        for pep, weights in progress_bar(self.tandem.items(), "Calculating scores"):
            if len(pep) > minlen:
                for spec in sample:
                    scores.append((pep, shared_peak(weights, spec.peaks, 1.2)))
        return heapq.nlargest(amount, scores, key=lambda t: t[1])



if __name__ == '__main__':
    import sys
    sample = MS2Spectrum.load_spectra(sys.argv[1], 2)
    try:
        db = ProteinDB2.load('ms2.db')
        save = False
    except Exception as e:
        print("Couldn't load ms2.db ({}), creating a new one".format(e))
        save = True
        db = ProteinDB2()
    
    try:
        print_scores(db.find_best_peptides(sample))
    except Exception as e:
        db.save()
        raise e
    
    if save:
        db.save('ms2.db')

