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

from ._core import EngineCore, EngineStatus, EngineConnectionError

from ..models._core import _Field

from ..models.fields import CharField,AutoField, IntegerField, DateField, DateTimeField, EmailField, BooleanField

from .common import Constants


class Engine(EngineCore):

    _column_types = {CharField:'text',
                     AutoField:'integer',
                     IntegerField:'integer',
                     DateField:'datetime',
                     DateTimeField:'datetime',
                     EmailField:'text',
                     BooleanField:'boolean'
                     }

    def __init__(self, dbpath):
        super().__init__(db_path=dbpath, shared=True, unique_per_thread=True)

    def _prepare(self):
        pass

    def start(self):
        """Start the db Engine - called by the user of the engine
        
        Concrete implementation must :
            keep Track of the EngineStatus
            use the Engine.connect method so that sharing options are honoured 
            Identify if the database is empty/new or not
        """

        new_db = False
        """Start the db Engine - connect to the db file"""
        if not self.db_path.exists():
            new_db = True

        # Try to connect to the database
        self.status = EngineStatus.Started
        self.connect()

        # Get any new db ready to run
        if not new_db and self.status == EngineStatus.Connected and self.status_db_ready():
            self.status = EngineStatus.Ready

        return self.is_connected()

    def status_db_ready(self):
        """ Use a technique - unknown as yet to prove that the database is Ready or not """
        return True

    def get_db_handle(self):
        """sqlite specific function to connect to the database"""

        if self.status != EngineStatus.Started:
            raise RuntimeError('Imternal Engine Error - db_handle called in incorrect state')
        try:
            return sqlite3.connect(str(self.db_path))
        except (IOError, OSError) as e:
            raise EngineConnectionError('Unable to connect to database : {}'.format(e.strerror))

    @property
    def db_connection(self):
        return super().handle

    @classmethod
    def column_name(cls_, field: _Field):
        """Generate appropriate SQL fragment for this field in a select statement"""
        return '"{}"'.format(field.db_column)

    @classmethod
    def column_type(cls_, field: _Field):
        """Generate appropriate SQL fragment for this field in a select statement"""
        type = cls_._column_types[field.__class__]
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