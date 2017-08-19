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

from enum import Enum
from pyorm.db.models._core import _Field

class EngineStatus(Enum):
    Stopped = 1 # Not started
    Started = 2 # start has been called - not connected
    Connected = 3 # Connected to db - but db is empty
    Ready = 4 # Db is ready for migrations etc
    Disconnected = 5

class SqlCommands(Enum):
    SELECT = 1
    CREATE = 2
    DELETE = 3
    DROP = 4
    ALTER = 5


class EngineException(Exception):
    pass

class EngineConnectionError(Exception):
    pass


#TODO - Rationalise this - it feels a mess - too much too and fro - I think.

class EngineCore(metaclass=ABCMeta):

    _connections_per_thread = None
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

        # As this gets populated it will be a dictionary of files - with a dictionary of threads
        if not EngineCore._connections_per_thread:
            EngineCore._connections_per_thread = defaultdict(self._per_file_connections)

        # Implement sharing across threads by ignoring the threading
        if self._shared:
            if self._unique_per_thread:
                self._thread_id = threading.get_ident()
            else:
                self._thread_id = None

        self._db_handle = None
        self.status = EngineStatus.Stopped

    def _per_file_connections(self):
        """Implement the dictionary of threads for each file"""
        return defaultdict(self.get_db_handle)

    def connect(self):
        """ Connect to the database - if not already connected

            Applies the various rules regarding shared connections
        """
        # Are we already connected
        if not self._db_handle:
            # If there is no sharing - get a new handle
            if not self._shared:
                try:
                    db_handle = self.get_db_handle()
                except:
                    self.status = EngineStatus.Disconnected
                    raise
                else:
                    self._db_handle = db_handle
            else:
                # Add a file into the connections list (if not there)
                # Add a thread for this file - and grab a handle if required

                self._db_handle = EngineCore._connections_per_thread[self._db_path][self._thread_id]

        EngineCore._ref_counts[self._db_handle] += 1
        self.status = EngineStatus.Connected
        return self._db_handle

    def disconnect(self):
        if self._db_handle is None:
            return False

        EngineCore._ref_counts[self._db_handle] -= 1
        if EngineCore._ref_counts[self._db_handle] == 0:
            del EngineCore._ref_counts[self._db_handle]
            self._db_handle = None
            self.status = EngineStatus.Disconnected
            return True
        else:
            return False

    def is_connected(self):
        return self.status in [EngineStatus.Connected, EngineStatus.Ready]

    def is_ready(self):
        return self.status == EngineStatus.Ready

    @abstractmethod
    def get_db_handle(self):
        """Get a new connnection reference - as required"""
        raise NotImplemented('\"get_db_handle\" Must be implemeneted on subclass')

    @abstractmethod
    def start(self):
        """Start the db Engine - called by the user of the engine"""
        raise NotImplemented('\"start\" Must be implemeneted on subclass')

    @property
    def is_empty(self):
        return self.is_empty

    @property
    def handle(self):
        return self._db_handle

    @property
    def db_path(self):
        return self._db_path

    @classmethod
    def reset(cls):
        """Force Resest the core data for the db Engine - use with care"""
        EngineCore._connections_per_thread = None
        EngineCore._ref_counts = defaultdict(int)

    @abstractmethod
    def start(self):
        """Start the engine - connect to database - connects etc"""
        raise NotImplemented('\"start\" Must be implemeneted on subclass')

    @abstractmethod
    def column_name(self, field: _Field):
        """Create the appropriate sql fragement for this field in a select statement"""
        raise NotImplemented('\"select_field\" must be implemented on subclasse')

    @abstractmethod
    def column_type(self, field: _Field):
        """Create the appropriate sql fragement for this field in a select statement"""
        raise NotImplemented('\"select_field\" must be implemented on subclasse')

    @abstractmethod
    def column_constraint(self, field: _Field):
        """Create the appropriate sql fragement for this field in a select statement"""
        raise NotImplemented('\"select_field\" must be implemented on subclasse')