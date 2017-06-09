"""MS2 scoring functions: Shared peaks and Sequest."""

import heapq
import math
from itertools import chain

from .db import *
from .spectra import *


class Scorer:
    def __init__(self, tolerance):
        self.tolerance = tolerance
    
    def score(self, tspec: TheoMs2Spectrum, espec: ExpMs2Spectrum):
        raise NotImplemented("score is not overriden")
    
    # Define preproc_espec if there is a need for preprocessing
    def preprocess_espec(self, espec: ExpMs2Spectrum):
        return espec


class SharedPeaks(Scorer):
    def score(self, tspec: TheoMs2Spectrum, espec: ExpMs2Spectrum):
        i, j, score = 0, 0, 0
        tp = tspec.peaks
        ep = espec.peaks
        while i != len(tp) and j != len(ep):
            if abs(tp[i] - ep[j][0]) <= self.tolerance:
                score += 1
            
            if (tp[i] < ep[j][0] and not i == len(tp)-1) or j == len(ep)-1:
                i += 1
            else:
                j += 1
        
        return score


class Sequest(Scorer):
    """Based on Eng1994 and Eng2008. Some differences:
    
      - Theoretical spectra in the entire package don't have intensities, so this scoring algo
        is no different. Eng1994 specifies some constant intensities based on the type of ion.
        (Eng 1994, page 5, but also an insightful comment 
        `here <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2738854/>`_ (search SEQUEST)) We 
        only use the main b and y ions, which are all considered to have (relative) 
        intensity 50.
        
      - We don't (always) group/compress the spectra in 'unit-sized bins', currently we use
        something like bins (but with more accuracy) of width tolerance/10.
    """
    
    def __init__(self, tolerance, num_windows=10, stepsize=1.0, steps=75):
        super().__init__(tolerance)
        self.num_windows = num_windows
        self.stepsize = stepsize
        self.steps = steps
    
    def preprocess_espec(self, espec, compress=True):
        # Preprocessing the peaks never seems to be fully described. The most important
        # thing to do (mentioned in both papers) is normalizing the intensities in a given
        # amount of fixed windows to 50 (or 100)
        ep = espec.peaks
        min_loc = min(ep, key=ExpMs2Spectrum.location)[0]
        max_loc = max(ep, key=ExpMs2Spectrum.location)[0]
        
        # only retain the 200 most intense peaks (Only in Eng1994)
        #ep = heapq.nlargest(200, ep, ExpMs2Spectrum.intensity)
        
        # extra sqrt (Only in Eng2008?)
        ep = [(loc, math.sqrt(intensity)) for loc, intensity in ep]
        
        # normalize in fixed amount of windows across the entire range (Eng1994 says 10)
        window_length = (max_loc - min_loc)/self.num_windows
        window_maximums = []
        i = 0
        for window in range(self.num_windows):
            window_end = min_loc + window_length*(window+1)
            window_max = 0.0
            while i < len(ep) and ep[i][0] <= window_end:
                window_max = max(window_max, ep[i][1])
                i += 1
            window_maximums.append(window_max)
        
        i = 0
        for window in range(self.num_windows):
            if window_maximums[window] == 0.0:
                continue
            window_rescale = 50.0/window_maximums[window]
            window_end = min_loc + window_length*(window+1)
            while i < len(ep) and ep[i][0] <= window_end:
                ep[i] = (ep[i][0], ep[i][1] * window_rescale)
                i += 1
        
        new_espec = ExpMs2Spectrum(espec.title, espec.pepmass, ep)
        # This is (very) specific to Eng2008
        new_espec.y_prime = self.y_prime(new_espec, compress)
        return new_espec
    
    def y_prime(self, espec, compress=True):
        #  y' = y_0 - (sum(y_t for t in [-75..-1, 1..75])/150)
        shifts = chain(frange(-self.steps * self.stepsize, 0, self.stepsize),
                       frange(self.stepsize, (self.steps+1) * self.stepsize, self.stepsize))
        resized_int = [-p[1]/(2*self.steps) for p in espec.peaks]
        shifted = sum(([(espec.peaks[i][0]+t, resized_int[i]) for i in range(len(espec.peaks))]
                            for t in shifts), [])
        
        if compress:
            # Shifted produces way too many points. While mathematically still correct (since
            # our dot_product is just a big sum anyway), it takes too much time. So, time for
            # a minimum amount of 'binning'
            shifted = sorted(shifted, key=ExpMs2Spectrum.location)
            locs = [shifted[0][0]]
            total = shifted[0][1]
            tol = self.tolerance / 10
            binned = []
            shifted_it = iter(shifted)
            next(shifted_it)  # skip first without making a whole new list
            for s in shifted_it:
                if s[0] > locs[0] + tol:
                    binned.append((sum(locs)/len(locs), total))
                    locs = [s[0]]
                    total = s[1]
                else:
                    locs.append(s[0])
                    total += s[1]
            
            return sorted(espec.peaks + binned, key=ExpMs2Spectrum.location)
        else:
            return sorted(espec.peaks + shifted, key=ExpMs2Spectrum.location)
        
    def score(self, tspec, espec):
        """This is basically the xcorr score. An alternative would be the 
        E-value, as suggested by Eng2008. It's based on the xcorr yet vastly
        more complex.
        """
        return dot_product(tspec.peaks, 50.0, espec.y_prime, self.tolerance)

