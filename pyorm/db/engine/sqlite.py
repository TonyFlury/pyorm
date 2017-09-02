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

from ._core import EngineCore

from ..models._core import _Field

from ..models import fields

from .common import Constants

import pyorm.core.exceptions as exceptions

import decimal
import datetime

from typing import Union, Type

class TruncDateSQLFunctions:
    """A Simple holder for the Trunc date functions

       Holding them as members of a class makes it easier to
       enumarate them without a separate module.
    """
    @staticmethod
    def splitdate(d, l):
        if not d:
            return None
        try:
            return '-'.join(d.split(' ')[0].split('-')[0:l] + ['1']*(3-l))
        except Exception as exc:
            print(str(exc))
            raise

    @staticmethod
    def splittime(d, l):
        if not d:
            return None
        try:
            return ':'.join(d.split(' ')[1].split(':')[0:l]+['00']*(3-l)).split('.')[0]
        except Exception as exc:
            raise

    @staticmethod
    def Truncyear( d ):
        d =  TruncDateSQLFunctions.splitdate(d, 1)
        return d


    @staticmethod
    def Truncmonth( d ):
        if not d:
            return d
        return TruncDateSQLFunctions.splitdate(d, 2)

    @staticmethod
    def Truncday( d ):
        if not d:
            return d
        return TruncDateSQLFunctions.splitdate(d, 3)

    @staticmethod
    def Trunchour( d ):
        if d:
            return TruncDateSQLFunctions.splitdate(d, 3) + ' ' + TruncDateSQLFunctions.splittime(d, 1)
        else:
            return None

    @staticmethod
    def Truncminutes( d ):
        if d:
            return TruncDateSQLFunctions.splitdate(d, 3) + ' ' + TruncDateSQLFunctions.splittime(d, 2)
        else:
            return None

    @staticmethod
    def Truncseconds(d):
        if d:
            return TruncDateSQLFunctions.splitdate(d, 3) + ' ' + TruncDateSQLFunctions.splittime(d, 3)
        else:
            return None

# SQLITE3 uses an adapter/coverter protocol to allow programs to define custom
# DB types

class DecimalAdapter:
    """Adapter for the decimal db_type"""
    def __init__(self, python_type):
        self._python_type = python_type

    def adapt(self, value):
        if self._python_type == decimal.Decimal and isinstance(value,(decimal.Decimal,)):
            return str(value)
        else:
            raise exceptions.pyOrmEngineAdapterError('InternalError : Unexpected value {} rec\'d in Decimal adapter'.format(value.__class__.__name__))

    def convert(self, data ):
        if self._python_type == decimal.Decimal:
            return self._python_type(str(data,'utf-8'))
        else:
            raise exceptions.pyOrmEngineAdapterError('InternalError : Unexpected value {} rec\'d in Decimal converter'.format(data.__class__.__name__))

class DurationAdapter:
    """Adapter for the decimal db_type"""
    def __init__(self,python_type):
        self._python_type = python_type

    def adapt(self, value):
        if self._python_type == datetime.timedelta and isinstance(value,(datetime.timedelta,)):
            return str('{td.days}:{td.seconds}:{td.microseconds}'.format(td=value))
        else:
            raise exceptions.pyOrmEngineAdapterError('InternalError : Unexpected value {} rec\'d in Duration adapter'.format(value.__class__.__name__))

    def convert(self, data):
        if self._python_type == datetime.timedelta:
            d,s,ms = map(int, data.split(b':'))
            return datetime.timedelta(days=d, seconds=s,microseconds=ms)
        else:
            raise exceptions.pyOrmEngineAdapterError('InternalError : Unexpected value {} rec\'d in Duration converter'.format(data.__class__.__name__))

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
    _need_adapters = {'decimal': DecimalAdapter,
                      'duration': DurationAdapter
                     }

    def prepare_engine(self, dbpath):
        # Register the adapters we need.
        for field_type, db_type in self.__class__._column_types.items():
            adapater_type = self.__class__._need_adapters.get(db_type, None)
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
            for method in TruncDateSQLFunctions.__dict__:
                if method.startswith('Trunc'):
                    con.create_function(method, 1, getattr(TruncDateSQLFunctions, method))

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