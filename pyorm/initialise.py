#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of initialise

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

from pathlib import Path
from pyorm.core.settingsmanager import SettingsManager
from contextlib import contextmanager

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '23 Aug 2017'

class Initialise:
    _sm = None
    def __init__(self, settings=None, overrides = None):
        if Initialise._sm :
            return
        else:
            Initialise._sm = self

        self._overrides = overrides if overrides else {}
        self._settings_file = (Path('.').absolute() / 'settings.py') if not settings else Path(settings)
        Initialise._sm = SettingsManager(settings_file=self._settings_file, **self._overrides)

    def __enter__(self):
        return self._sm.__enter___()

    def __exit__(self, exc_type, exc_val, exc_tb):
        Initialise._sm = None
        return self._sm.__exit__()

    @classmethod
    def get_sm(cls):
        return cls._sm
