#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of compiler.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
import pyorm.core.exceptions as exceptions
from functools import wraps

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '31 Aug 2017'

LOOKUP_SEP = '__'

def RegisterLookUp(compiler_class, lookup_name):
    def outer_wrapper( func ):
        @wraps(func)
        def inner_wrapper( field_name,value):
            return func(field_name,value)

        compiler_class.register_lookup(lookup_name, inner_wrapper)
        return inner_wrapper
    return outer_wrapper

class Compiler:
    _lookups = {}

    def __init__(self, engine, obj):
        self._engine = engine
        self._obj = obj

    @classmethod
    def register_lookup(cls, name, func):
        cls._lookups[name] = func

    def lookup(self, lookup, value):
        parts = lookup.split(LOOKUP_SEP)
        lookup_callable = self._lookups.get(parts[-1],None)
        if lookup_callable is None:
            raise exceptions.UnknownLookup('Unknown field lookup {}'.format(parts[-1]))

        # Extract a dotted field name
        field = '.'.join(parts[0:-1])

        # Generate a dotted list of field names need to get to this field
        if len(parts) > 1:
            tables = ['.'.join(parts[0:i+1]) for i, t in enumerate(parts[0:-2])]
        else:
            tables = []

        return (tables, lookup_callable(field,value))