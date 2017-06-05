
from .spectra import *
from .db import *
from .scoring import *

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

try:
    sp = SharedPeaks(1.2)
    print_scores(db.find_best_peptides(sample, scorer))
except Exception as e:
    if save:
        db.save(db_loc)
    raise e

if save:
    db.save(db_loc)
