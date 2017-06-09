"""MS2 spectra, theoretical ionization and database"""

import heapq
from itertools import repeat, chain

from ms.util import *
from ms.MS1 import ProteinDB, shared_peak


class Ms2Spectrum:
    def __init__(self, title, pepmass):
        self.title = title
        self.pepmass = float(pepmass)


class TheoMs2Spectrum(Ms2Spectrum):
    """Theoretical MS2 Spectrum.
    Here, self.peaks is just a list of peak locations.
    """
    
    @classmethod
    def from_sequence(cls, s, ionizer=None):
        """Not used in the analysis, useful for visualisation and comparison."""
        if ionizer is None:
            from .db import Ionizer
            ionizer = Ionizer()
        return cls(title=s,
                   pepmass=peptide_mass(s),
                   peaks=ionizer(s))
    
    def __init__(self, title, pepmass, peaks):
        super().__init__(title, pepmass)
        self.peaks = sorted(peaks)
    
    def plot(self, color='red'):
        import matplotlib.pyplot as plt
        plt.stem(self.peaks, [50]*len(self.peaks), color, label=self.title)


class ExpMs2Spectrum(Ms2Spectrum):
    """Experimental MS2 Spectrum.
    Here, self.peaks is a list of (location, intensity) tuples.
    """
    
    location = lambda t: t[0]
    intensity = lambda t: [1]
    
    def __init__(self, title, pepmass, peaks, **kwargs):
        super().__init__(title, pepmass)
        self.peaks = sorted(peaks, key=lambda t: t[0])
    
    def plot(self, color='blue'):
        import matplotlib.pyplot as plt
        plt.stem([p[0] for p in self.peaks], [p[1] for p in self.peaks], color, label=self.title)
    
    @classmethod
    @simple_progress('Loading MS2 spectra')
    def load_spectra(cls, fname, maximum=float('inf')) -> '[ExpMs2Spectrum]':
        """Parse a MGF file"""
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
                    
                    spectra.append(cls(metadata.pop('TITLE'), metadata.pop('PEPMASS').split(' ')[0],
                                       peaks, **metadata))
                    if len(spectra) >= maximum:
                        break
        return spectra

    @staticmethod
    def _key_value(line):
        parts = line.strip().split('=', 1)
        if len(parts) < 2:
            return None
        return parts[0].strip().upper(), parts[1].strip()
