# -*- coding: utf-8 -*-
import inspect
from flask import g
import types
import decorator
import pickle

def context_cache():
    if not hasattr(g, 'context_cache') or type(g.context_cache) != types.DictType:
        g.context_cache = {}
    return g.context_cache


def kwargs_to_args(f, *args, **kwargs):
        #: Inspect the arguments to the function
        #: This allows the memoization to be the same
        #: whether the function was called with
        #: 1, b=2 is equivilant to a=1, b=2, etc.
        new_args = []
        arg_num = 0
        m_args = inspect.getargspec(f)[0]

        for i in range(len(m_args)):
            if m_args[i] in kwargs:
                new_args.append(kwargs[m_args[i]])
            elif arg_num < len(args):
                new_args.append(args[arg_num])
                arg_num += 1
        return tuple(new_args)

def make_cache_key(f, *args, **kwargs):
        return "%s%s" % (f.__name__, kwargs_to_args(f, *args, **kwargs))


def context_cached():
    @decorator.decorator
    def context_cached_function(f, *args, **kwargs):
        cache_key = make_cache_key(f, *args, **kwargs)
        cache = context_cache()

        rv = cache.get(cache_key)
        if rv is None:
            rv = f(*args, **kwargs)
            cache[cache_key] = rv
        else:
            pass

        return rv
    return context_cached_function


def redis_cached(timeout=30):
    @decorator.decorator
    def redis_cached_function(f, *args, **kwargs):
        cache_key = make_cache_key(f, *args, **kwargs)
        cache = g.redis

        try:
            rv = pickle.loads(cache.get(cache_key))
        except:
            rv = f(*args, **kwargs)
            cache.setex(cache_key, pickle.dumps(rv), timeout)

        return rv
    return redis_cached_function