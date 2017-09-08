#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of _core

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

import threading
from abc import abstractmethod, ABCMeta
from collections import defaultdict

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '29 Jul 2017'

from contextlib import contextmanager

from enum import Enum
from pyorm.db.models._core import _Field
from pyorm.core.exceptions import ConnectionError


class SqlCommands(Enum):
    SELECT = 1
    CREATE = 2
    DELETE = 3
    DROP = 4
    ALTER = 5



class EngineCore(metaclass=ABCMeta):

    class Connection:
        """Wrapper to the database connection to  pass through everything other than the close

            The Wrapper has it's own close method which only closes the real connection if the ref count drops to zero.
        """
        def __init__(self, handle, engine, shared=True):
            self._handle = handle
            self._engine = engine
            self._shared = shared

        def __getattr__(self, item):
            return getattr(self._handle, item)

        def close(self):
            if self._shared:
                self._engine.__class__._ref_counts[self] -= 1
                if self._engine.__class__._ref_counts[self] == 0:
                    del self._engine.__class__._ref_counts[self]
                    del self._engine.__class__._connections_per_thread[self._engine._db_path][
                        self._engine._thread_id]
                    return self._handle.close()
            else:
                return self._handle.close()

        @property
        def handle(self):
            return self._handle

    _connections_per_thread = dict()
    _ref_counts = defaultdict(int)

    def __init__(self, db_path, shared=True, unique_per_thread=True):
        """A database agnostic base for the db specific handle managers

        :param db_path: The path to the database file
        :param shared: Whether db connections are shared or if multiple connections are used.
        :param unique_per_thread: Whether db connections are shared across threads
        
        If shared is True and unique_per_thread is True then
            One handle is returned per thread.
            
        If shared is True and unique_per_thread is False then
            One handle is shared across all threads in the process
            
        if shared is False then each handle attempt results in a new handle.
        """
        self._db_path = db_path
        self._shared = shared
        self._unique_per_thread = unique_per_thread

        # Implement sharing across threads by ignoring the threading
        if self._shared:
            if self._unique_per_thread:
                self._thread_id = threading.get_ident()
            else:
                self._thread_id = None

        self.prepare_engine(db_path)

    @classmethod
    @abstractmethod
    def CreateTemporaryDb(cls, shared=True, unique_per_thread=True):
        """Specialised class method to create a temporary db instance"""
        raise NotImplemented

    @abstractmethod
    def prepare_engine(self, path):
        raise NotImplemented

    @abstractmethod
    def get_connection(self):
        raise NotImplemented

    def connect(self):
        """ Connect to the database - if not already connected

            Applies the various rules regarding shared connections
        """
        # If there is no sharing - get a new handle
        if not self._shared:
            try:
                db_handle = self.Connection(self.get_connection(),engine=self, shared = self._shared)
            except ConnectionError as exc:
                raise exc from None
            else:
                return db_handle
        else:
            # Add a file into the connections list (if not there)
            # Add a thread for this file - and grab a handle if required
            # cannot use a default dict here as this is a class variable but has a per instance default function
            if self._db_path not in EngineCore._connections_per_thread:
                EngineCore._connections_per_thread[self._db_path] = dict()

            if self._thread_id not in EngineCore._connections_per_thread[self._db_path]:
                EngineCore._connections_per_thread[self._db_path][self._thread_id] = self.Connection(self.get_connection(), engine=self)

            connection = EngineCore._connections_per_thread[self._db_path][self._thread_id]

        EngineCore._ref_counts[connection] += 1
        return connection

    @classmethod
    def open_connections(cls, db_path):
        for thread, connections in cls._connections_per_thread.get(db_path,{}).items():
            yield (thread, connections)

    @property
    def db_path(self):
        return self._db_path

    @classmethod
    def reset(cls):
        """Force Resest the core data for the db Engine - use with care"""
        EngineCore._connections_per_thread = dict()
        EngineCore._ref_counts = defaultdict(int)

    @abstractmethod
    def column_name(self, field: _Field):
        """Create the appropriate sql fragement for this field in a select statement"""
        raise NotImplemented('\"select_field\" must be implemented on subclass')

    @abstractmethod
    def column_type(self, field: _Field):
        """Create the appropriate sql fragement for this field in a select statement"""
        raise NotImplemented('\"select_field\" must be implemented on subclass')

    @abstractmethod
    def column_constraint(self, field: _Field):
        """Create the appropriate sql fragement for this field in a select statement"""
        raise NotImplemented('\"select_field\" must be implemented on subclass')

    def resolve_name(self, name, model=None, joins=None):
        pass

    def resolve_lookup(self, name, value, model=None, joins=None):
        pass