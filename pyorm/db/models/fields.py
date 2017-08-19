#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of fields.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
from typing import Union
from pyorm.db.engine.common import Constants
from ._core import _Field, AutoField            # Import Autofield so everything is in one place
from .mappings import ForeignKey                # Import ForeignKey so everything is in one place

from pyorm.core.exceptions import pyOrmVaidationError, pyOrmFieldCoercionError
from pyorm.core.validators import EmailValidator

from pathlib import Path

import datetime
import decimal
import numbers

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '01 Aug 2017'

class BinaryField(_Field):
    def __init__(self,  **kwargs):
        """A character string field"""
        super(BinaryField, self).__init__( python_type=bytearray, **kwargs)

class BooleanField(_Field):
    def __init__(self,  **kwargs):
        """A character string field"""
        super(BooleanField, self).__init__( python_type=bool, **kwargs)

class CharField(_Field):
    def __init__(self, blank:bool=True, max_length:Union[int,None]=None, **kwargs):
        """A character string field"""
        self._max_length = max_length if max_length else int(Constants['MAX_TEXT_LENGTH'])
        self._blank =  blank
        super(CharField, self).__init__(python_type=str, **kwargs)

    @property
    def max_length(self):
        return self._max_length

    def can_be_blank(self):
        return self._blank

    def validate_value(self, value:str):
        """Local generic validation for dealing with field specific validation attributes"""

        if  not value and not self.can_be_blank():
            raise pyOrmVaidationError('value is blank/None but \'blank\' attribute is False')

        if value is None:
            return

        if len(value) > self.max_length:
            raise pyOrmVaidationError('value is longer than specified max_length {}'.format(self.max_length))


class DateField(_Field):
    """Define the type of data required for a char field in SQL data"""
    def __init__(self,  **kwargs):
        """A character string field"""
        super(DateField, self).__init__( python_type=datetime.date, allow_callable_default = True, **kwargs)


class DateTimeField(_Field):
    """Define the type of data required for a char field in SQL data"""
    def __init__(self, **kwargs):
        """A character string field"""
        super(DateTimeField, self).__init__( python_type=datetime.datetime, allow_callable_default = True, **kwargs)


class DecimalField(_Field):
    def __init__(self, **kwargs):
        """A character string field"""
        super(DecimalField, self).__init__( python_type=decimal.Decimal, **kwargs)

    def convert_type(self, value, new_type):
        try:
            return decimal.Decimal(value)
        except (ValueError, TypeError, decimal.InvalidOperation) as exc:
            raise pyOrmFieldCoercionError('Unable to convert {} to decimal : Invalid syntax'.format(type(value).__name__)) from exc


class DurationField(_Field):
    def __init__(self,   **kwargs):
        """A character string field"""
        super(DurationField, self).__init__( python_type=datetime.timedelta, **kwargs)


class EmailField(CharField):
    def __init__(self,   **kwargs):
        if 'max_length' in kwargs:
            del kwargs['max_length']

        super(EmailField, self).__init__( validator=EmailValidator(), **kwargs)


class FileField(_Field):
    def __init__(self,   **kwargs):
        """A character string field"""
        super(FileField, self).__init__( python_type=Path, **kwargs)


class FloatField(_Field):
    def __init__(self,   **kwargs):
        """A character string field"""
        super(FloatField, self).__init__( python_type=float, **kwargs)

    def convert_type(self, value, new_type):
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise pyOrmFieldCoercionError('Invalid value : {}'.format(str(exc)))


class IntegerField(_Field):
    # noinspection PyShadowingBuiltins
    def __init__(self, **kwargs):
        """ An Integer field"""
        super(IntegerField, self).__init__( python_type=int, **kwargs)

    def convert_type(self, value, new_type):
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise pyOrmFieldCoercionError('Invalid value : {}'.format(str(exc)))

class TimeField(_Field):
    def __init__(self,   **kwargs):
        """A character string field"""
        super(TimeField, self).__init__( python_type=datetime.time, **kwargs)





