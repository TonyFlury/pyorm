#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of mappings.py

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
__created__ = '15 Aug 2017'

from pyorm.db.models import models, _core


class ForeignKey(_core._Mapping):
    def __init__(self, *args, **kwargs):
        super(ForeignKey, self).__init__(*args, python_type = models.Model, **kwargs)

    def _attributes_valid(self):

        assert issubclass(self._othermodel, models.Model)

        if not issubclass(self._othermodel, models.Model):
            raise ValueError("'othermodel' attrribute on field '{n}' must be a valid Model".format(n=self.name))

        self._db_column = self._othermodel.__table__ + "_id"

        # check that the to_field is set correctly
        if self._to_field:
            # Ensure that the field exists on the other model
            if self._to_field not in self._othermodel.db_fields():
                raise ValueError(" Invalid settings for field '{n}' : '{c}' is not a field on the '{m}' model".format(
                    n=self.name,
                    c=self._to_field,
                    m=self._othermodel.__name__))
            else:
                return
        else:
            # Search for primary field in the other model
            self._to_field = self._othermodel.primary_name()

    def is_valid(self, value):
        return isinstance(value, models.Model)