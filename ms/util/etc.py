
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
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir,
                                        os.pardir, 'data', location))

def nice_lines(f):
    for l in f.readlines():
        if not l.isspace():
            yield l.strip()


# Output (both terminal and files)
# ================================

from .table import as_rest_table

def print_scores(scores, title=str):
    print('')
    data = [('#', 'score', 'name')]
    data += [(i+1, sc[1], title(sc[0])) for i, sc in enumerate(scores)]
    print(as_rest_table(data))
    print('')


def progress_bar(l, text, length=None, size=40):
    """Shows a progress bar while iterating over a list.
    Avoids printing all the time and making your program IO-bound.
    """
    
    modulo = max(round((length or len(l))/size), 1)
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



# Various utilities (kind of my own copy-paste standard library)
# ==============================================================

from collections import defaultdict

identity = lambda x: x

def frange(start, end=None, stepsize=1.0):
    if end is None:
        end = start
        start = 0.0
    
    i = start
    while i < end:
        yield i
        i += stepsize


def dot_product(x_loc: list, x_val: float, y: list, tolerance=1.0):
    i, j = 0, 0
    total = 0.0
    while i != len(x_loc) and j != len(y):
        if abs(x_loc[i] - y[j][0]) <= tolerance:
            total += x_val * y[j][1]
        
        if (x_loc[i] < y[j][0] and not i == len(x_loc)-1) or j == len(y)-1:
            i += 1
        else:
            j += 1
    
    return total


class GeneratorLength:
    def __init__(self, g, l):
        self.g = g
        self.l = l
    
    def __iter__(self):
        return self.g
    
    def __len__(self):
        return self.l
    
    def __getattr__(self, item):
        return getattr(self.g, item)


def generator_length(_len_func):
    def decorator(func, len_func=_len_func):
        @wraps(func)
        def wrapper(*a, **kw):
            gen = func(*a, **kw)
            return GeneratorLength(gen, len_func(*a, **kw))
        return wrapper
    return decorator


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

