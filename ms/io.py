
import os
from Bio import SeqIO


def data_loc(location):
    return os.path.join(os.path.dirname(__file__), '../data', location)
