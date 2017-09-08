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
    """Base exception class for all pyorm exceptions"""
    pass

class pyOrmVaidationError(pyOrmBaseException):
    """Internal exception to signifiy failed validation"""
    pass

class pyOrmFieldCoercionError(pyOrmBaseException):
    """Internal exception to signifiy failed validation"""
    pass


class ModelCreation(pyOrmBaseException):
    """Base for public exceptions related to the creation of objects"""
    pass

class PrimaryKeyError(ModelCreation):
    """Errors related to the models primary key (too many, or none at all"""
    pass

class ManagerCreationError(ModelCreation):
    """Errors related to the managers"""
    pass


class pyOrmEngineException(pyOrmBaseException):
    """Exceptions raised by the database Engine"""
    pass

class ConnectionError(pyOrmEngineException):
    """Public API Exception for all connection errors"""
    pass

class pyOrmEngineAdapterError(pyOrmEngineException):
    """Internal Exceptions if database Adapter fails"""
    pass

class ColumnError(pyOrmEngineException):
    """Public API Exception when columns from Engine don't match columns in models"""
    pass

class pyOrmEngineDataError(pyOrmEngineException):
    """Generic execption base for data errors"""
    pass

class QuerySetError(pyOrmBaseException):
    pass

class CompileError(QuerySetError):
    pass

class NoTables(CompileError):
    pass

class UnknownLookup(CompileError):
    pass

class DoesNotExist(QuerySetError):
    """Public API exception when expected data does not exist"""
    pass

class MultipleObjects(QuerySetError):
    """Public API exception when Two many rows/objects are fetched"""
    pass

class JoinError(QuerySetError):
    """Public API exception when there is an error creating a join"""
    pass

class LimitsError(QuerySetError):
    """Public API exception when there is an error in the Limits value"""
    pass

class NotModfiable(QuerySetError):
    """Public API exception when the query cannot be modified"""
    pass