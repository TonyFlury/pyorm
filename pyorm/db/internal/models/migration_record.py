#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of migration_record.py

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

from pyorm.models.fields import CharField, DateField

from db.models.models import Model


class MigrationRecord(Model):
    migration_id = CharField(length=40)
    application_date = DateField()

