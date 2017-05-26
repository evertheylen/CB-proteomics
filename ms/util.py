
import os
from functools import wraps


# Input (both terminal and files)
# ===============================

def data_loc(location):
    return os.path.join(os.path.dirname(__file__), '../data', location)

def nice_lines(f):
    for l in f.readlines():
        if not l.isspace():
            yield l.strip()


# Output (both terminal and files)
# ================================

def print_scores(scores, title=str):
    print('\n    # |   score   | name')
    print(  '------+-----------+---------------------')
    for i, (r, score) in enumerate(scores):
        print('{: >5} | {:.7f} | {}'.format(i+1, score, title(r)))



def progress_bar(l, text, size=40):
    """Shows a progress bar while iterating over a list.
    Avoids printing all the time and making your program IO-bound.
    """
    
    modulo = round(len(l)/size)
    progress = 0
    for i, item in enumerate(l):
        if i%modulo == 0:
            print('\r' + text + '\t  [' + '#'*progress + ' '*(size-progress) + ']', end='', flush=True)
            progress += 1
        yield item
    print('\r' + text + '\t  Done.' + ' '*size)
    

def simple_progress(text):
    """Similar to `progress_bar`, but for when you want to wait on the result of a function
    instead of monitoring a for loop. Therefore, this is a decorator.
    """
    
    def decorator(func):
        @wraps(func)
        def new_func(*a, **kw):
            print('\r' + text + '\t  ... ', end='')
            res = func(*a, **kw)
            print('\r' + text + '\t  Done.')
            return res
        return new_func
    return decorator


# Various utilities
# =================

from collections import defaultdict

class multimap(defaultdict):
    def __init__(self, *a, **kw):
        super().__init__(set, *a, **kw)
    
    def flat_items(self):
        for k, values in self.items():
            for v in values:
                yield k, v
                
    def flat_values(self):
        for values in self.values():
            for v in values:
                yield v
    
    def flat_len(self):
        s = 0
        for v in self.values():
            s += len(v)
        return s
    
    def flatten(self):
        d = {}
        for k, v in self.items():
            if len(v) != 1:
                raise NotFlat(v)
            d[k] = v.pop()
        return d

