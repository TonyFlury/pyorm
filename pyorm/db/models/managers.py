#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of managers.py

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
__created__ = '26 Aug 2017'



class Manager:
    def __init__(self, name='', model=None):
        self._name = name
        self._model = model

    @property
    def model(self):
        return self._model

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if self.name:
            raise AttributeError('Cannot change name attribute once set')
        self._name = new_name
        # Todo Add all relevant methods to the Manager - including filters etc



#Todo write ForiegnKey, One to One and Many to Many Managers