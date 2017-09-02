#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of utils

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '29 Aug 2017'


class Lazy:
    def __init__(self, *args, **kwargs):
        """A base class designed to simply record it's args and kwargs - for later processing"""
        self._args  = args
        self._kwargs = kwargs

    def __str__(self):
        """The Str representation always mirrors back the all - with the kwargs sorted alphabetically

        Py3.5 doesn't preserve the order of kwargs, and therefore the kwargs are sorted as part of the str """
        params = [repr(x) for x in self._args]
        params += ['{key}={value!r}'.format(key=k,value=repr(self._kwargs[k])) for k in sorted([k for k in self._kwargs])]
        return '{}({})'.format(self.__class__.__name__, ','.join(params))

    def __eq__(self, other):
        """Lazies are equal if their strings are equal:

        Use strings so don't have to worry deep comparisons of all items"""
        return str(self) == str(other)

    def __repr__(self):
        """repr and str are the same"""
        return str(self)

    def __hash__(self):
        return hash(str(self))



class Annotation(Lazy):
    """A class for adding other classes to a query set - aggregates etc"""
    pass

class Related(Lazy):
    pass