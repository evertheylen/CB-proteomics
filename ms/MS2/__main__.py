
import argparse

from .spectra import *
from .db import *
from .scoring import *
from ms.util import *

parser = argparse.ArgumentParser(description='MS2 database search')
parser.add_argument('-d', '--database', help='FASTA file to use for the database', 
                                        default=ProteinDB2.default_file)
parser.add_argument('-p', '--pickled', help='File to use to write the database to, pickled. '
                                            'Overrides the database argument if found.',
                                       default=None)
parser.add_argument('-s', '--scorer', help="Scorer to be used, eval'd. Options are SharedPeaks and Sequest, "
                                           "both need a first argument of (absolute) tolerance.",
                                      default="Sequest(0.6)")
parser.add_argument('-a', '--amount', help='Amount of results', type=int, default=10)
parser.add_argument('sample', help='MS2 spectra file, MGF format')
args = parser.parse_args()

sample = ExpMs2Spectrum.load_spectra(args.sample)

use_pickle = (args.pickled is not None)
save = False

if use_pickle:
    try:
        db = ProteinDB2.load(args.pickled)
        save = False
    except Exception as e:
        print("\nCouldn't load database: {}, creating a new one".format(e))
        save = True
        db = ProteinDB2(args.database)
else:
    db = ProteinDB2(args.database)

try:
    sp = eval(args.scorer)
    results = []
    for espec in progress_bar(sample, 'Calculating scores'):
        results.append((espec, db.find_best_peptides(espec, sp, amount=args.amount)))
    
    print("")
    print("Results")
    print("=======")
    print("")
    
    for espec, scores in results:
        print(espec.title)
        print('-' * len(espec.title))
        print('')
        print_scores(scores)
        print('\n')
    
except Exception as e:
    if save:
        db.save(args.pickled)
    raise e

if save:
    db.save(args.pickled)
