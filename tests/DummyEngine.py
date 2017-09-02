#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of DummyEngine

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
from unittest.mock import MagicMock

from pyorm.db.engine._core import EngineCore
from pyorm.db.models._core import _Field

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '27 Aug 2017'


class DummyEngine(EngineCore):
    """Concrete Engine implementation, with mocked connections"""
    _step = 0

    def __init__(self, db_path, shared=True, unique_per_thread=True):
        super().__init__(db_path, shared=shared, unique_per_thread=unique_per_thread)

    def get_connection(self):
        DummyEngine._step += 1
        con = MagicMock(name='Connection {}'.format(DummyEngine._step))
        con.value.return_value = DummyEngine._step
        return con

    @classmethod
    def reset(cls):
        cls._step = 0
        super().reset()

    # Dummy methods to match abstract methods - they don't need to do anything here.
    def column_constraint(self, field: _Field):
        pass

    def column_name(self, field: _Field):
        pass

    def column_type(self, field: _Field):
        pass

    @classmethod
    def CreateTemporaryDb(cls, shared=True, unique_per_thread=True):
        pass

    def prepare_engine(self, path):
        pass


class MockedEngine(MagicMock(spec=EngineCore)):
    """A Completely mocked DB Engine"""
    pass