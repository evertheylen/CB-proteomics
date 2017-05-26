
import os
from functools import wraps

try:
    import cPickle as pickle
    print("using cPickle instead of pickle")
except ImportError:
    import pickle


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
    print('')


def progress_bar(l, text, size=40):
    """Shows a progress bar while iterating over a list.
    Avoids printing all the time and making your program IO-bound.
    """
    
    modulo = round(len(l)/size)
    progress = 0
    for i, item in enumerate(l):
        if i%modulo == 0:
            print(progress_bar_start.format(text) + '#'*progress + ' '*(size-progress) + ']', end='', flush=True)
            progress += 1
        yield item
    print(progress_end.format(text) + ' '*size)

progress_bar_start = '\r{: <40}  ['
progress_start     = '\r{: <40}  ... '
progress_end       = '\r{: <40}  Done. '

def simple_progress(text):
    """Similar to `progress_bar`, but for when you want to wait on the result of a function
    instead of monitoring a for loop. Therefore, this is a decorator.
    """
    
    def decorator(func):
        @wraps(func)
        def new_func(*a, **kw):
            print(progress_start.format(text), end='')
            res = func(*a, **kw)
            print(progress_end.format(text))
            return res
        return new_func
    return decorator


# Pickling help
# =============

class Pickled:
    def save(self, fname = None):
        fname = fname or self._loaded_from
        text = 'Saving {} to {}'.format(type(self).__name__, fname)
        print(progress_start.format(text), end='')
        import gc
        with open(fname, 'wb') as f:
            gc.disable()
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
            gc.enable()
        print(progress_end.format(text))
    
    @classmethod
    def load(cls, fname):
        text = 'Loading {} from {}'.format(cls.__name__, fname)
        print(progress_start.format(text), end='')
        import gc
        with open(fname, 'rb') as f:
            gc.disable()
            data = pickle.load(f)
            gc.enable()
        data.__class__ = cls
        data._loaded_from = fname
        print(progress_end.format(text))
        return data



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


def memoize(f):
    """Memoization decorator for functions taking one or more arguments."""
    # Source: https://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/#c1
    class memodict(dict):
        def __init__(self, f):
            self.f = f
        def __call__(self, *args):
            return self[args]
        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret
    return memodict(f)

