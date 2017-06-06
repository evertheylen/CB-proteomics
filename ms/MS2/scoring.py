"""
MS2 scoring functions
"""

import heapq
import math

from .db import *
from .spectra import *

class Scorer:
    def __init__(self, tolerance):
        self.tolerance = tolerance
    
    def score(self, tspec: TheoMs2Spectrum, espec: ExpMs2Spectrum):
        raise NotImplemented("score is not overriden")
    
    # Define preproc_espec if there is a need for preprocessing
    # def preproc_espec(self, espec: ExpMs2Spectrum): ...


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
    """Based on Eng1994 and Eng2008"""
    
    #   source: Eng 1994 (page 5), but also an insightful comment here (search SEQUEST): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2738854/
    
    def preproc_espec(self, espec):
        # Preprocessing the peaks never seems to be fully described. The most important
        # thing to do (mentioned in both papers) is normalizing the intensities in a given
        # amount of fixed windows to 50 or 100
        ep = espec.peaks
        min_loc = min(ep, key=ExpMs2Spectrum.location)[0]
        max_loc = max(ep, key=ExpMs2Spectrum.location)[0]
        
        # only retain the 200 most intense peaks (Only in Eng1994)
        #ep = heapq.nlargest(200, ep, ExpMs2Spectrum.intensity)
        
        # extra sqrt (Only in Eng2008)
        ep = [(loc, math.sqrt(intensity)) for loc, intensity in ep]
        
        # normalize in fixed amount of windows accros the entire range (Eng1994 says 10)
        num_windows = 10
        window_length = (max_loc - min_loc)/num_windows
        window_maximums = []
        i = 0
        for window in range(num_windows):
            window_end = min_loc + window_length*(window+1)
            window_max = 0.0
            while i < len(ep) and ep[i][0] <= window_end:
                window_max = max(window_max, ep[i][1])
                i += 1
            window_maximums.append(window_max)
        
        i = 0
        for window in range(num_windows):
            window_end = min_loc + window_length*(window+1)
            window_rescale = 50.0/window_maximums[window]
            while i < len(ep) and ep[i][0] <= window_end:
                ep[i] = (ep[i][0], ep[i][1] * window_rescale)
                i += 1
        
        return ExpMs2Spectrum(espec.title, espec.pepmass, ep)

def xcorr(x: 'theoretical', y: 'experimental', tolerance=1.2):
    i = 0
    j = 0
    while i != len(sample) and j != len(weights):
        if abs(sample[i][0] - weights[j]) <= tolerance:
            score += 1 #sample[i][1]
        
        if (sample[i][0] < weights[j] and not i == len(weights)-1) or j == len(weights)-1:
            i += 1
        else:
            j += 1
    
    return score


