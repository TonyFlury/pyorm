# /usr/bin/env python
"""
# DBmodels : Implementation of model

Summary :
    <summary of module/class being tested>
Use Case :
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

import pyorm.core.exceptions as exceptions
from pyorm.core.settingsmanager import SettingsManager
from ._core import _Field, _Mapping, _ModelMetaClass
from ..engine.common import ImportEngine

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '23 Sep 2014'


class Model( metaclass=_ModelMetaClass):

    def __init__(self, **kwargs):
        super(Model, self).__init__()

        # Need to create every field
        for field_name, field_definition in self.db_fields():
            default = field_definition.default() if field_definition.callable_default else field_definition.default

            value = default if (field_name not in kwargs) else kwargs[field_name]

            setattr(self, field_name, value)

        super().__setattr__('__dirty', True)

    def primary_name(self):
        """Returns the primary key for this instance - this is a _Field instance - not a raw value

        :rtype : _FieldABC instance (i.e. a subclass of _FieldABC or _Field
        """
        return self.__class__._primary

    @classmethod
    def primary_field(cls):
        return cls._primary

    @classmethod
    def dependencies(cls):
        """  Return a list of the Models which this model is dependent on
        """
        return cls._dependencies

    def __setattr__(self, key, value):

        # Todo Needs to be changed for a manager field

        field = self.db_field_by_name(key)

        if not field:
            super().__setattr__(key, value)
            return

        # If a field hasn't been set yet then the attribute will still be the class attr
        if not field.is_mutable() and not super().__getattribute__(key) is field:
            raise AttributeError('Cannot change value of immutable field {} once set'.format(key))

        try:
            field.verify_value(value)
        except AttributeError as exc:
            raise exc from None
        except Exception as exc:
            raise AttributeError('Unknown error while validating value for {} field : {}'.format(self.name, str(exc)))

        super().__setattr__(key, value)
        super().__setattr__('__dirty', True)

    @classmethod
    def db_fields(cls):
        """Iterate around the field defines and captured

          returns a 2-tuple of (name, field instance) for every field
        """
        yield from ((field_name,instance) for field_name,instance in cls._db_fields.items())

    @classmethod
    def db_field_by_name(cls_, name:str):
        return cls_._db_fields.get(name, None)

    @classmethod
    def db_column_to_attr_name(cls_, db_column:str):
        """Look up to translate a specific db_column name into the attribute name"""
        if db_column in cls_._columns_to_attr:
            return cls_._columns_to_attr[db_column].name
        else:
            return None

    @classmethod
    def _db_data_to_model_attrs(cls_, db_data=None):
        """Convert a dictionary from an database engine into a set of attributes for a model class constructor """
        if not db_data:
            return {}

        attrs = {}
        for column_name, value in db_data.items():
            attr_name = cls_.db_column_to_attr_name(db_column=column_name)
            if attr_name is None:
                raise exceptions.ColumnError('Unexpected column from database: column \'{}\' is not known on the \'{}\' model'.format(column_name, cls_.__name__)) from None
            attrs[attr_name] = value
        return attrs

    @classmethod
    def _check_field_names(cls_, field_names):
        for name in field_names:
            if cls_.db_field_by_name(name=name) is None:
                raise AttributeError('Unknown field name: \'{}\' is not a field on \'{}\' model'.format(name, cls_.__name__))

    @classmethod
    def table_name(cls):
        return cls._table_name

    @classmethod
    def get_relationshup(cls, manager_name):
        """Finds the named manager, returns a 3-tuple

           [0] The related model(s) in this manager
           [1] The field on this model
           [2] The field on the related model
        """
        pass