#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of settingsmanager.py

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
__created__ = '01 Aug 2017'

import sys
from pathlib import Path

import importlib.util
from importlib.machinery import ModuleSpec

class DummyModule(dict):
    def __init__(self, kwargs):
        super().__init__([(k,v) for k,v in kwargs.items()])

    def __getattribute__(self, item):
        try:
            return super().__getitem__(item)
        except:
            raise


class SettingsManager():
    _obj = None

    def __new__(cls, *args, **kwargs):
        if cls._obj:
            return cls._obj
        cls._obj =  super().__new__(cls)
        return cls._obj

    def __init__(self, settings_file:Path, dummy_module:bool=False, overrides=None):
        self._syspath = sys.path
        self._settings_file = settings_file if settings_file else Path('./settings.py')
        self._dummy_module = dummy_module if dummy_module else False
        self._settings = self.import_settings()
        self._overrides = overrides if overrides else {}

    def get(self, item:str):
        if self._settings:
            return self._overrides.get(item, self._settings.__dict__.get( item,None))
        else:
            raise AttributeError

    def import_settings(self):
        if not self._settings_file.exists():
            if not self._dummy_module:
                raise ImportError('No module @ {}'.format(self._settings_file))

            module = importlib.util.module_from_spec(ModuleSpec(name='settings',loader=None))
            exec('', module.__dict__)
            sys.modules['settings'] = module
            self._settings = module
        else:
            spec = importlib.util.spec_from_file_location('settings', str(self._settings_file.absolute()))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules['settings'] = module
            self._settings = module
        return module

    @property
    def file_source(self):
        return self._settings_file

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self._settings = None
        self.__class__._obj = None
        if 'settings' in sys.modules:
            del sys.modules['settings']

    @classmethod
    def get_sm(cls):
        return cls._obj