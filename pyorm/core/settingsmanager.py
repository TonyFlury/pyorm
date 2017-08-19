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

from importlib import import_module

def import_from_path(file_name):
    sys.path = [str(Path(file_name).parent)] + sys.path
    mod = import_module('settings')
    sys.path = sys.path[1:]
    return mod

class SettingsManager():
    def __init__(self, settings_file):
        self._settings = import_from_path(file_name=settings_file)

    def __getattribute__(self, item):
        return getattr(object.__getattribute__(self, '_settings'), item)
