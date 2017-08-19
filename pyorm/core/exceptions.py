#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of exceptions

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
__created__ = '17 Aug 2017'

class pyOrmBaseException(Exception):
    pass

class pyOrmVaidationError(pyOrmBaseException):
    pass

class pyOrmFieldCoercionError(pyOrmBaseException):
    pass

class InvalidField(pyOrmBaseException):
    pass

class UnknownCondition(pyOrmBaseException):
    pass