
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

def print_scores(scores: '[(name, score)]', title=str, normalize=True):
    if len(scores) == 0:
        print("No data")
        return
    
    norm_factor = 1
    if normalize:
        norm_factor /= max(scores, key=lambda t: t[1])[1]
    
    print('')
    data = [('#', 'score', 'name')]
    data += [(i+1, sc[1]*norm_factor, title(sc[0])) for i, sc in enumerate(scores)]
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



# SortedCollection, taken from https://code.activestate.com/recipes/577197-sortedcollection/

from bisect import bisect_left, bisect_right

class SortedCollection:
    '''Sequence sorted by a key function.

    SortedCollection() is much easier to work with than using bisect() directly.
    It supports key functions like those use in sorted(), min(), and max().
    The result of the key function call is saved so that keys can be searched
    efficiently.

    Instead of returning an insertion-point which can be hard to interpret, the
    five find-methods return a specific item in the sequence. They can scan for
    exact matches, the last item less-than-or-equal to a key, or the first item
    greater-than-or-equal to a key.

    Once found, an item's ordinal position can be located with the index() method.
    New items can be added with the insert() and insert_right() methods.
    Old items can be deleted with the remove() method.

    The usual sequence methods are provided to support indexing, slicing,
    length lookup, clearing, copying, forward and reverse iteration, contains
    checking, item counts, item removal, and a nice looking repr.

    Finding and indexing are O(log n) operations while iteration and insertion
    are O(n).  The initial sort is O(n log n).

    The key function is stored in the 'key' attibute for easy introspection or
    so that you can assign a new key function (triggering an automatic re-sort).

    In short, the class was designed to handle all of the common use cases for
    bisect but with a simpler API and support for key functions.

    >>> from pprint import pprint
    >>> from operator import itemgetter

    >>> s = SortedCollection(key=itemgetter(2))
    >>> for record in [
    ...         ('roger', 'young', 30),
    ...         ('angela', 'jones', 28),
    ...         ('bill', 'smith', 22),
    ...         ('david', 'thomas', 32)]:
    ...     s.insert(record)

    >>> pprint(list(s))         # show records sorted by age
    [('bill', 'smith', 22),
     ('angela', 'jones', 28),
     ('roger', 'young', 30),
     ('david', 'thomas', 32)]

    >>> s.find_le(29)           # find oldest person aged 29 or younger
    ('angela', 'jones', 28)
    >>> s.find_lt(28)           # find oldest person under 28
    ('bill', 'smith', 22)
    >>> s.find_gt(28)           # find youngest person over 28
    ('roger', 'young', 30)

    >>> r = s.find_ge(32)       # find youngest person aged 32 or older
    >>> s.index(r)              # get the index of their record
    3
    >>> s[3]                    # fetch the record at that index
    ('david', 'thomas', 32)

    >>> s.key = itemgetter(0)   # now sort by first name
    >>> pprint(list(s))
    [('angela', 'jones', 28),
     ('bill', 'smith', 22),
     ('david', 'thomas', 32),
     ('roger', 'young', 30)]

    '''

    def __init__(self, iterable=(), key=None):
        self._given_key = key
        key = (lambda x: x) if key is None else key
        decorated = sorted((key(item), item) for item in iterable)
        self._keys = [k for k, item in decorated]
        self._items = [item for k, item in decorated]
        self._key = key

    def _getkey(self):
        return self._key

    def _setkey(self, key):
        if key is not self._key:
            self.__init__(self._items, key=key)

    def _delkey(self):
        self._setkey(None)

    key = property(_getkey, _setkey, _delkey, 'key function')

    def clear(self):
        self.__init__([], self._key)

    def copy(self):
        return self.__class__(self, self._key)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def __iter__(self):
        return iter(self._items)

    def __reversed__(self):
        return reversed(self._items)

    def __repr__(self):
        return '%s(%r, key=%s)' % (
            self.__class__.__name__,
            self._items,
            getattr(self._given_key, '__name__', repr(self._given_key))
        )

    def __reduce__(self):
        return self.__class__, (self._items, self._given_key)

    def __contains__(self, item):
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return item in self._items[i:j]

    def index(self, item):
        'Find the position of an item.  Raise ValueError if not found.'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].index(item) + i

    def count(self, item):
        'Return number of occurrences of item'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].count(item)

    def insert(self, item):
        'Insert a new item.  If equal keys are found, add to the left'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        self._keys.insert(i, k)
        self._items.insert(i, item)

    def extend(self, items):
        for item in items:
            k = self._key(item)
            i = bisect_left(self._keys, k)
            self._keys.insert(i, k)
            self._items.insert(i, item)

    def insert_right(self, item):
        'Insert a new item.  If equal keys are found, add to the right'
        k = self._key(item)
        i = bisect_right(self._keys, k)
        self._keys.insert(i, k)
        self._items.insert(i, item)

    def remove(self, item):
        'Remove first occurence of item.  Raise ValueError if not found'
        i = self.index(item)
        del self._keys[i]
        del self._items[i]

    def find(self, k):
        'Return first item with a key == k.  Raise ValueError if not found.'
        i = bisect_left(self._keys, k)
        if i != len(self) and self._keys[i] == k:
            return self._items[i]
        raise ValueError('No item found with key equal to: %r' % (k,))

    def find_le(self, k):
        'Return last item with a key <= k.  Raise ValueError if not found.'
        i = bisect_right(self._keys, k)
        if i:
            return self._items[i-1]
        raise ValueError('No item found with key at or below: %r' % (k,))

    def find_lt(self, k):
        'Return last item with a key < k.  Raise ValueError if not found.'
        i = bisect_left(self._keys, k)
        if i:
            return self._items[i-1]
        raise ValueError('No item found with key below: %r' % (k,))

    def find_ge(self, k):
        'Return first item with a key >= equal to k.  Raise ValueError if not found'
        i = bisect_left(self._keys, k)
        if i != len(self):
            return self._items[i]
        raise ValueError('No item found with key at or above: %r' % (k,))

    def find_gt(self, k):
        'Return first item with a key > k.  Raise ValueError if not found'
        i = bisect_right(self._keys, k)
        if i != len(self):
            return self._items[i]
        raise ValueError('No item found with key above: %r' % (k,))
    
    def find_between(self, _min, _max):
        'Own addition: find items in certain (inclusive) range'
        i = bisect_left(self._keys, _min)
        j = bisect_right(self._keys, _max)
        return [self._items[k] for k in range(i, j)]
    

import unittest

class SortedCollectionBetweenTests(unittest.TestCase):
    def setUp(self):
        self.sc = SortedCollection([-50, 1, 2, 5, 43, 456])
    
    def test_all(self):
        self.assertEqual(self.sc.find_between(-50, 456), list(self.sc))
    
    def test_start(self):
        self.assertEqual(self.sc.find_between(-51, 0.9), [-50])
        self.assertEqual(self.sc.find_between(-51, -50.1), [])
    
    def test_end(self):
        self.assertEqual(self.sc.find_between(456, 456.1), [456])
        self.assertEqual(self.sc.find_between(456.1, 456.2), [])
