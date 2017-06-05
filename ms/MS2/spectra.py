"""MS2 spectra, theoretical ionization and database
"""

import heapq
from itertools import repeat, chain

from .etc import *
from .util import *
from .MS1 import ProteinDB, shared_peak


# Spectrum classes
# ----------------

class Ms2Spectrum:
    def __init__(self, title, pepmass):
        self.title = title
        self.pepmass = pepmass


class TheoMs2Spectrum(Ms2Spectrum):
    """Theoretical MS2 Spectrum
    self.peaks is just a list of peak locations
    """
    
    def __init__(self, title, pepmass, peaks):
        super().__init__(title, pepmass)
        self.peaks = sorted(peaks)
    

class ExpMs2Spectrum(Ms2Spectrum):
    """Experimental MS2 Spectrum
    self.peaks is a list of (location, intensity)
    """
    
    def __init__(self, title, pepmass, peaks, **kwargs):
        super().__init__(title, pepmass)
        self.peaks = sorted(peaks, key=lambda t: t[0])
    
    # Parsing
    
    @staticmethod
    def _key_value(line):
        parts = line.strip().split('=', 1)
        if len(parts) < 2:
            return None
        return parts[0].strip().upper(), parts[1].strip()
    
    @classmethod
    @simple_progress('Loading MS2 spectra')
    def load_spectra(cls, fname, maximum=float('inf')) -> '[ExpMs2Spectrum]':
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
                        kv = cls._key_value(peak)
                        if kv:
                            metadata[kv[0]] = kv[1]
                        else:
                            location, intensity = peak.split()
                            peaks.append((float(location.strip()), float(intensity.strip())))
                    
                    spectra.append(cls(metadata.pop('TITLE'), metadata.pop('PEPMASS'),
                                       peaks, **metadata))
                    if len(spectra) >= maximum:
                        break
        return spectra



# Ionization and fragmentation
# ----------------------------

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



# Database and searches
# ---------------------

class ProteinDB2(Pickled):
    default_file = data_loc('uniprot-human-reviewed-trypsin-november-2016.fasta')
    
    def __init__(self, fname = None, missed_cleavages=1, ionizer=Ionizer()):
        fname = fname or self.default_file
        self.targets = ProteinDB(fname, missed_cleavages).proteins
        self.decoys = ProteinDB(fname, missed_cleavages, reverse=True).proteins
        # We already know the peptides, now we have to cut it up once more
        self.tandem = {}
        self._process_proteins(self.targets.proteins, 'TARGET')
        self._process_proteins(self.decoys.proteins, 'DECOY ')
    
    def _process_proteins(self, proteins, tag):
        for prot in progress_bar(proteins, 'Splitting in ions, tagged `{}`'.format(tag)):
            for peptide in prot.chunks:
                if peptide not in self.tandem:
                    title = tag + ' ' + pep
                    self.tandem[peptide] = TheoMs2Spectrum(title = tag + ' ',
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
        return heapq.nlargest(amount, self.peptides_scores(sample, tolerance), key=lambda t: t[1])



# Main function
# -------------

if __name__ == '__main__':
    db_loc = 'ms2.db'
    import sys
    sample = ExpMs2Spectrum.load_spectra(sys.argv[1], 2)
    try:
        db = ProteinDB2.load(db_loc)
        save = False
    except Exception as e:
        print("Couldn't load ms2.db ({}), creating a new one".format(e))
        save = True
        db = ProteinDB2()
    
    from .scoring import *
    
    try:
        sp = SharedPeaks(1.2)
        print_scores(db.find_best_peptides(sample, scorer))
    except Exception as e:
        if save:
            db.save(db_loc)
        raise e
    
    if save:
        db.save(db_loc)

