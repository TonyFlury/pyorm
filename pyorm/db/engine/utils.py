#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of utils.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

from functools import wraps

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '31 Aug 2017'



def RegisterComparison(engine_class, lookup_name):
    """Decorator define a comparison function to support comparise between field and value"""
    def outer_wrapper( func ):
        @wraps(func)
        def inner_wrapper( field_name,value):
            return func(field_name,value)
        engine_class.register_comparison(lookup_name, inner_wrapper)
        return inner_wrapper
    return outer_wrapper

def RegisterFunction(engine_class, lookup_name):
    """Decorator define a lookup function to support transformation of a SQL field"""
    def outer_wrapper( func ):
        @wraps(func)
        def inner_wrapper(*args):
            return func(*args)
        engine_class.register_function(lookup_name, inner_wrapper)
        return inner_wrapper
    return outer_wrapper

def RegisterAdapter(engine_class, field_type_name):
    def outerwrapper(cls):
        @wraps(cls)
        def innerwrapper(python_type):
            return cls(python_type)
        engine_class.register_adapter(field_type_name, innerwrapper)
        return innerwrapper
    return outerwrapper
