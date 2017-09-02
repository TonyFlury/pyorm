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

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '31 Aug 2017'

from .compiler import RegisterLookUp, Compiler

@RegisterLookUp(Compiler, 'exact')
def exact(field_name, value ):
    return "{}={}".format(field_name, value)
