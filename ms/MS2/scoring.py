"""
MS2 scoring functions
"""

from .MS2 import *

class Scorer:
    def __init__(self, tolerance):
        self.tolerance = tolerance
    
    def score(self, tspec: TheoMs2Spectrum, espec: ExpMs2Spectrum):
        raise NotImplemented("score is not overriden")
    
    # Define preproc_espec if there is a need for preprocessing
    # def preproc_espec(self, espec: ExpMs2Spectrum): ...


class SharedPeaks:
    def score(self, tspec: TheoMs2Spectrum, espec: ExpMs2Spectrum):
        i, j, score = 0, 0, 0
        tp = tspec.peaks
        ep = espec.peaks
        while i != len(tp) and j != len(ep):
            if abs(tp[i] - ep[j][0]) <= self.tolerance:
                score += 1
            
            if (tp[i] < ep[j] and not i == len(tp)-1) or j == len(ep)-1:
                i += 1
            else:
                j += 1
        
        return score


class Sequest:
    #   source: Eng 1994 (page 5), but also an insightful comment here (search SEQUEST): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2738854/
    pass

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


