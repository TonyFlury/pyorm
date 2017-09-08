#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of sqlite3

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
import sqlite3

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '29 Jul 2017'

from abc import abstractmethod

from .core import EngineCore

from ..models._core import _Field

from ..models import fields

from .common import Constants
from .utils import RegisterComparison, RegisterAdapter, RegisterFunction

import pyorm.core.exceptions as exceptions

import decimal
import datetime


class Engine(EngineCore):

    _column_types = {fields.AutoField: 'integer',
                     fields.BinaryField:'blob',
                     fields.BooleanField: 'boolean',
                     fields.CharField:'text',
                     fields.DecimalField:'decimal',
                     fields.DateField:'date',
                     fields.DateTimeField:'timestamp',
                     fields.DurationField:'duration',
                     fields.EmailField:'text',
                     fields.FloatField: 'float',
                     fields.IntegerField: 'integer',
                     }

    _comparisons = {}
    _functions = {}
    _adapters = {}
    _lookups = {}

    @classmethod
    def register_comparison(cls, name, comparison_callable):
        cls._comparisons[name] = comparison_callable

    @classmethod
    def register_function(cls, name, function_callable):
        cls._functions[name] = function_callable

    @classmethod
    def register_adapter(cls, name, adater_class):
        cls._adapters[name] = adater_class

    def prepare_engine(self, dbpath):
        # Adapters get added to the sqlite library rather than a specific connection
        for field_type, db_type in self.__class__._column_types.items():
            adapater_type = self.__class__._adapters.get(db_type, None)
            if adapater_type:
                adapter = adapater_type(field_type.python_type())
                sqlite3.register_adapter(field_type.python_type(), adapter.adapt)
                sqlite3.register_converter(db_type,adapter.convert)


    @classmethod
    def CreateTemporaryDb(cls, shared=True, unique_per_thread=True):
        return cls(dbpath=':memory:', shared=True, unique_per_thread=True)

    def get_connection(self):
        """sqlite specific function to connect to the database"""
        try:
            con = sqlite3.connect(str(self.db_path), detect_types=sqlite3.PARSE_DECLTYPES)
            for method_name, method in self.__class__._functions.items():
                con.create_function(method_name, -1, method)

            con.row_factory = sqlite3.Row
            return con
        except (IOError, OSError) as e:
            raise exceptions.ConnectionError('Unable to connect to database : {}'.format(e.strerror))


    @classmethod
    def column_name(cls_, field: _Field):
        """Generate appropriate SQL fragment for this field in a select statement"""
        return '"{}"'.format(field.db_column)

    @classmethod
    def column_type(cls_, field: _Field):
        """Generate appropriate SQL fragment for this field in a select statement"""
        type = cls_._column_types.get(field.__class__,'text')
        segment = '{type}'.format(type =type)
        return segment

    @classmethod
    def column_constraint(cls_, field: _Field):
        constraint_segment = {lambda f:f.not_null() and not f.is_primary():'NOT NULL',
                                  lambda f: hasattr(f,'max_length') and f.max_length and f.max_length != Constants['MAX_TEXT_LENGTH']:
                                      'CHECK (typeof("{f.db_column}") = "{column_type}" and length("{f.db_column}") <= {f.max_length})',
                                  lambda f:f.is_unique() and not f.is_primary(): 'UNIQUE',
                                  lambda f:f.is_primary() : 'PRIMARY KEY'
                                  }

        segments = []
        for k,v in constraint_segment.items():
            if k(field):
                yield v.format(f=field, column_type=cls_._column_types[field.__class__])

#-----------------------------------------------------------------
#
# Engine specific functions for field comparisions - called
# only when fields have been fully resolved
#
#----------------------------------------------------------------
@RegisterComparison(Engine, 'exact')
def exact(field_name, value ):
    return "{} = {!r}".format(field_name, value)

@RegisterComparison(Engine, 'iexact')
def iexact(field_name, value ):
    return "{} = {!r}".format(field_name, value)

@RegisterComparison(Engine, 'gte')
def gte(field_name, value ):
    return "{} >= {!r}".format(field_name, value)

@RegisterComparison(Engine, 'gt')
def gt(field_name, value ):
    return "{} > {!r}".format(field_name, value)

@RegisterComparison(Engine, 'lt')
def lt(field_name, value ):
    return "{} < {!r}".format(field_name, value)

@RegisterComparison(Engine, 'lte')
def lte(field_name, value ):
    return "{} <= {!r}".format(field_name, value)

@RegisterComparison(Engine, 'contains')
def contains(field_name, value ):
    return "{} like \'%{}%\'".format(field_name, value)

@RegisterComparison(Engine, 'startswith')
def startswith(field_name, value ):
    return "{} like \'{}%\'".format(field_name, value)

@RegisterComparison(Engine, 'endswith')
def startswith(field_name, value ):
    return "{} like \'%{}\'".format(field_name, value)

#-----------------------------------------------------------------
#
# Database Adapters
#
# sqlite3 uses adapters which can add new column types to the database
# Each Adapter needs to implement an adapt and a convert method
#
#-----------------------------------------------------------------
class Adapter:
    """Base adapter class"""
    def __init__(self, python_type):
        self._python_type = python_type

    @abstractmethod
    def adapt(self, value):
        """Convert the value to the representation to be stored into the database"""
        raise NotImplementedError

    @abstractmethod
    def convert(self, value):
        """Convert the bytes value from the database to the relevant python type"""
        raise NotImplementedError

@RegisterAdapter(Engine,'decimal')
class DecimalAdapter(Adapter):
    """Adapter for the decimal db_type

      Decimals are stored as strings in the database
    """

    def adapt(self, value):
        """Convert the value to the representation to be stored into the database"""
        if self._python_type == decimal.Decimal and isinstance(value,(decimal.Decimal,)):
            return str(value)
        else:
            raise exceptions.pyOrmEngineAdapterError('InternalError : Unexpected value {} rec\'d in Decimal adapter'.format(value.__class__.__name__))

    def convert(self, data ):
        """Convert the bytes value from the database to the relevant python type"""
        if self._python_type == decimal.Decimal:
            return self._python_type(str(data,'utf-8'))
        else:
            raise exceptions.pyOrmEngineAdapterError('InternalError : Unexpected value {} rec\'d in Decimal converter'.format(data.__class__.__name__))

@RegisterAdapter(Engine,'duration')
class DurationAdapter(Adapter):
    """Adapter for the duration db_type

      Durations are stored as a string  '<days>:<seconds>:<microseconds>' in the database
    """

    def adapt(self, value):
        """Convert the value to the representation to be stored into the database"""
        if self._python_type == datetime.timedelta and isinstance(value,(datetime.timedelta,)):
            return str('{td.days}:{td.seconds}:{td.microseconds}'.format(td=value))
        else:
            raise exceptions.pyOrmEngineAdapterError('InternalError : Unexpected value {} rec\'d in Duration adapter'.format(value.__class__.__name__))

    def convert(self, data):
        """Convert the bytes value from the database to the relevant python type"""
        if self._python_type == datetime.timedelta:
            d,s,ms = map(int, data.split(b':'))
            return datetime.timedelta(days=d, seconds=s,microseconds=ms)
        else:
            raise exceptions.pyOrmEngineAdapterError('InternalError : Unexpected value {} rec\'d in Duration converter'.format(data.__class__.__name__))


#----------------------------------
#
# TruncDate functions -
# By Default dates are actually stored and returned as text from the db
#
#-----------------------------------
def splitdate(date_str=None, level=1):
    """Split a date string

    :param date_str: The ISO date string YYYY-DD-MM[ HH:MM:SS.UUU]
    :param level: A value between 1 & 3 determining which part to remove -
              date parts removed are replaced with '1'
    :return:
    """
    return ('-'.join(date_str.split(' ')[0].split('-')[0:level] + ['1'] * (3 - level))) if date_str else None

def splittime(datetime_str=None, level=1):
    """Split a timeString

    :param date_str: The ISO date string YYYY-DD-MM[ HH:MM:SS.UUU]
    :param level: A value between 1 & 3 determining which part to remove -
              date parts removed are replaced with '00
              microsecond part is ALWAYS removed '
    :return:
    """
    return (':'.join(datetime_str.split(' ')[1].split(':')[0:level] + ['00'] * (3 - level)).split('.')[0]) if datetime_str else None

@RegisterFunction(Engine, 'TruncYear')
def TruncYear(the_date):
    """Truncate the date to the Year only - month and day are replaced with 1, time section is removed"""
    return splitdate(date_str=the_date, level=1)

@RegisterFunction(Engine, 'TruncMonth')
def Truncmonth(date_str):
    """Truncate the date to the Year & month only - day is replaced with 1, time section is removed"""
    return splitdate(date_str=date_str, level=2)

@RegisterFunction(Engine, 'TruncDay')
def Truncday(date_str):
    """Truncate the date to the Year, month & day only - time section is removed"""
    return splitdate(date_str=date_str, level=3)

@RegisterFunction(Engine, 'TruncHour')
def Trunchour(datetime_str):
    """Truncate the datetime to the hour - minutes and seconds are replaced with 00, microseconds are removed"""
    return (splitdate(date_str=datetime_str, level=3) + ' ' + splittime(datetime_str=datetime_str, level=1)) if datetime_str else None

@RegisterFunction(Engine, 'TruncMinutes')
def Truncminutes(datetime_str):
    """Truncate the datetime to the Minute - seconds are replaced with 00, microseconds are removed"""
    return (splitdate(date_str=datetime_str, level=3) + ' ' + splittime(datetime_str=datetime_str, level=2)) if datetime_str else None

@RegisterFunction(Engine, 'TruncSeconds')
def Truncseconds(datetime_str):
    """Truncate the datetime to the Second - seconds are replaced with 00, microseconds are removed"""
    return (splitdate(date_str=datetime_str, level=3) + ' ' + splittime(datetime_str=datetime_str, level=3)) if datetime_str else None
