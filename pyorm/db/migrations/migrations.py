#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of migrations.py

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



class Migration():
    def __init__(self, initial=False, dependencies=None, operations=None):
        self._initial = initial
        self._dependencies = dependencies if dependencies else []
        self._operations = operations if operations else []

    def execute(self):
        pass

class CreateModel():
    def __init__(self, name, fields):
        pass