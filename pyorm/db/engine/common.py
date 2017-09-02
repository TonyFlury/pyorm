#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of common.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

import importlib.util

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '01 Aug 2017'

Constants = {
    'MAX_TEXT_LENGTH':1000,
    }

class ImportEngine:
    _inst = None
    def __new__(cls, *args, **kwargs):
        if cls._inst is None:
            cls._inst =  super().__new__(cls)

        return cls._inst

    def __init__(self, settings):
        self._module = None
        self._engine_cls = None
        self._settings = settings
        self._engine_inst = None
        if settings:
            class_name = settings.get('engine')
            module_name, cls_name = '.'.join(class_name.split('.')[:-1]), class_name.split('.')[-1]
            self._module = importlib.import_module(name=module_name)
            self._engine_cls = getattr(self._module, cls_name)
            self._engine_inst = self._engine_cls(self._settings.get('database'))

    def engine_cls(self):
        return self._engine_cls

    def engine_inst(self):
        return self._engine_inst