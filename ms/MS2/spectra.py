"""MS2 spectra, theoretical ionization and database
"""

import heapq
from itertools import repeat, chain

from ms.util import *
from ms.MS1 import ProteinDB, shared_peak


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
    
    def plot(self):
        import matplotlib.pyplot as plt
        plt.stem(self.peaks, [1]*len(self.peaks))

class ExpMs2Spectrum(Ms2Spectrum):
    """Experimental MS2 Spectrum
    self.peaks is a list of (location, intensity)
    """
    
    location = lambda t: t[0]
    intensity = lambda t: [1]
    
    def __init__(self, title, pepmass, peaks, **kwargs):
        super().__init__(title, pepmass)
        self.peaks = sorted(peaks, key=lambda t: t[0])
    
    def plot(self):
        import matplotlib.pyplot as plt
        plt.stem([p[0] for p in self.peaks], [p[1] for p in self.peaks])
    
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

