#!/usr/bin/env python
#
# DBmodels : Implementation for _base.py
# 
# <Module Summary statement>
#

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '21 Oct 2014'

"""
# DBmodels : Implementation of _base.py

Summary : 
    Implementation of base classes and meta classes for the models module

Use Case : 
    As a Developer I want A consistent set of base classes and meta-classes So that I have a reusable and
    extensible code base

Testable Statements :
    Can I implement a base class for data base Fields
    Can I implement a base class for mapping fields
    Can I implement a base class for all my Models
"""
import os.path

from typing import TypeVar,Type, Union

from pyorm.core.exceptions import pyOrmVaidationError, pyOrmFieldCoercionError
from pyorm.core.validators import ValidatorBase

OBJ = TypeVar('OBJ')
VALIDATOR = Union[ValidatorBase,None]
class _Field():
    """ Base class for any new field object - encapsulates the fundamental attributes and methods for every field
    """
    def __init__(self, default:OBJ=None,  # The default value of this column
                 null:bool=True,  # Whether this field can be null
                 unique:bool=False,  # Whether this field must be unique
                 db_column:str=None,  # The Database column for this field
                 primary:bool=False,  # Whether this field is the primary key
                 indexed:bool=False, # Whether this field is indexed
                 python_type:Type = None, # The python type for this field
                 mutable:bool = True,
                 validator:VALIDATOR = None,
                 allow_callable_default:bool = False,
                 *args, **kwargs  # Any left over arguments - should be none
    ):
        """Base class to define a field which will be mapped to a database column on a specific table

        :param default : The default value for this field
        :param null: True if this field can be set to None/Null
        :param unique: True if this field can be unique
        :param db_column : The alternative name for this column in the database
        :param primary: True if this field is the primary key for this table
        :param indexed : True if this field is indexed
        :param python_type: The python type for this field
        :param allow_callable_default: whether the default value can be a callable
        :param mutable: Whether this field can be changed once created
        :param validator: callable to implement more complex validation.
        :param args: Extra args - should be empty - included for completion
        :param kwargs: Extra Kwargs - should be empty - included for completion
                This class is intended to be sub-classed into specific types of fields. Customisation :

        Can be customised :

        _attributes_valid : Checks the combination of column attributes,
                    uses _check_value to ensure that all the items in the choices list are valid for this field type
                    and that the default value is both a valid type and is on the choices list.
                    _Field.validate_attribute_settings()

        _check_value : Checks that a specific value is valid based on the defined column attributes
                     By default this checks that :
                     1) The value is allowed based on null attribute
                     2) That the value is of the correct type
                     3) That the value is is the choices list
                    _Field._check_value(self, value_to_check, ignore_choices=False, ignore_not_null=False):
                            skip_choices_check - skip the choices check (# 2 as above)
                            skip_null_check - skip the not_null check (#1 as above)

        One instance of this will exist per model - so it does not contain any per row data.
        """
        if len(kwargs):
            raise AttributeError('Unexpected arguements on {cls_name}: {args}'.format(cls_name=self.__class__.__name__,
                                                                                     args=','.join(x for x in kwargs)))

        assert len(args) == 0
        assert len(kwargs) == 0

        super(_Field, self).__init__()

        self._name = None
        self._default = default
        self._not_null = not null
        self._db_column = db_column
        self._unique = unique
        self._primary = primary
        self._python_type = python_type if python_type else object
        self._mutable = mutable
        self._validator = validator

        self._default_callable = default if (allow_callable_default and callable(default)) else None

        # If indexed is not specified then always index primary keys.
        if indexed:
            self._indexed = indexed
        else:
            self._indexed = self._primary

        if self.not_null() and self.default is None:
            raise AttributeError(
                'Default value is None, but \'null\' attribute is False')

        if self.python_type and self._default and not self._default_callable:
            if not isinstance(self._default, (self.python_type)):
                try:
                    self._default = self.convert_type(self._default, self._python_type)
                except pyOrmFieldCoercionError as exc:
                    if str(exc):
                        raise AttributeError(str(exc)) from None
                    else:
                        raise AttributeError('Default \'{}\' value is not of expected type: expecting {}'.format(type(self._default).__name__,self._python_type.__name__)) from None

        # Field validator method expected to handle any inputs including None and empty (string etc)
        try:
            self.validate_value(self._default)
        except pyOrmVaidationError as exc:
            raise AttributeError( 'Invalid Default value : {}'.format(str(exc))) from None

        # External validator method expected to handle only truthy inputs - i.e. not None and not empty (string etc)
        if self._default and self._validator:
            try:
                self._validator(self._default)
            except pyOrmVaidationError as exc:
                raise AttributeError('Invalid Default value : {}'.format(str(exc))) from None

    def is_unique(self):
        return self._unique

    def is_primary(self):
        """ If this field is the primary key for this table"""
        return self._primary

    def is_indexed(self):
        """Is this field going to be indexed"""
        return self._indexed

    def not_null(self):
        return self._not_null

    def is_mutable(self):
        return self._mutable

    @property
    def python_type(self):
        return self._python_type

    @property
    def name(self):
        """Set the name of this Field - derived from the actual class attribute being defined.

            Used as the db_column attribute if not set separately
            Can only be set once.
        """
        return self._name

    @name.setter
    def name(self, value):
        """Set the name of this Field - derived from the actual class attribute being defined.

            Used as the db_column attribute if not set separately
            Can only be set once.
        """
        if self._name:
            raise AttributeError("Cannot change the name attribute of {cls} once set".format(
                cls=self.__class__.__name__)) from None

        self._name = value
        self._db_column = self._db_column if self._db_column else self._name

    @property
    def db_column(self):
        """The column name being used in the database table - derived from the name if not set separately"""
        return self._db_column

    @property
    def default(self):
        """The default value for this field - set in the database, and the initial value of  the attribute"""
        return self._default

    def validate_value(self, value):
        """Rauses no exception if the value is valid for this field
         """
        return

    def convert_type(self, value, new_type):
        """Can be overriden by sub-class to allow coercion of one type to another
            
            Returns the coerced value if it can be coerced
            Raises FieldCoercionException if coercion is not allowed.
        """
        if not isinstance(value, new_type):
            raise pyOrmFieldCoercionError

        return value

class _Mapping(_Field):
    """Mixim to record the information required for a ForeignField, OneToMany or ManyToMany mapping"""
    def __init__(self, othermodel=None, to_field=None, *args, **kwargs):
        """Any field which allows a handle between table/models should sub class from this class

        :param othermodel: The other model that this model will link to
        :param to_field: The field on the other model that this links to.

        This mixim is simply for consistent storage - no functionality implemented
        """
        self._othermodel = othermodel
        self._to_field = to_field
        super(_Mapping, self).__init__(*args,**kwargs)

    def other_model(self):
        return self._othermodel

    def to_field(self):
        return self._to_field

class AutoField(_Field):
    def __init__(self, *args, **kwargs):
        if 'default' in kwargs:
            raise AttributeError('Cannot set default value for Autofield')
        super(AutoField, self).__init__(*args, python_type=int, primary=True, unique=True, null=False, mutable=False, default=0,**kwargs)

    def _check_value(self, new_value, old_value=None, skip_choices_check=False, skip_null_check=False):
        if old_value is not None:
            raise ValueError("Cannot change the value of AutoField '{n}' once set".format(n=self.name))
        else:
            return super(AutoField, self)._check_value(new_value, old_value, skip_choices_check=True)

    def _full_repr(self, value):
        return str(value)

    def _debug_repr(self, value):
        return str(value)

    def is_valid(self, value):
        return isinstance(value, int)

    def _sql_type(self):
        return "INTEGER"

#TODO - Simplify the ModelMetaClass - if _Field are descriptiors than don't need to translate class variables into instance attributes or try to STore their db details.

#TODO - Move validation from Model instantiation into descriptor instantiation - only thing Model needs to do is provide access to any meta info and set the name fields
class _ModelMetaClass(type):
    """Meta class for any Model instance

       This meta-class identifies all of the class attributes which are defined as Fields, and records them as
       entries in a separate _db_model_fields_metadata dictionary.
       It also sets the name field for the _Field instance, and explicitly validates the instance.
                Validation is explicit (rather than at construction) so that errors can contain the field name
       Ensures that initial set up of the bindings is done once when each class is created, rather than when
       each instance is created
    """

    _models = {}

    def __new__(mcs, cls_name, bases, cls_dict):
        """A meta class for customised creation of all Model subclasses

            Detects all class attributes which are subclasses of the _Field class, and builds a list of
                        these as metadata. More efficient to do this once when the class is defined, then to do
                        it each time an instance is instantiated.
                        Records the attribute name against each _Field instance, used as the default column name.
            Identifies 

            Builds default entries for __db_path__, __table__ and __name__ class attributes.


        """
        # Invoked when a new class is defined - i.e. when a class is compiled

        # Only do the complex stuff when doing subclasses of Model
        # Enables the models to just sub-class Model (without worrying about metaclass)

        if cls_name == "Model":
            return type.__new__(mcs, cls_name, bases, cls_dict)


        # Auto create the class attributes that the model needs - includes :
        # metadata for the various fields
        # class attributes for db_path, table_name and model name
        # shadow attributes for primary field and dependencies


        # Class attributes for the __db_path__, __table__ and __name__
        cls_dict["__db_path__"] = cls_dict.get("__db_path__", os.path.join(os.getcwd(), "sql.db"))
        cls_dict["__table__"] = cls_dict.get("__table__", cls_name)
        cls_dict["__name__"] = cls_name


        # Extract the class attributes which are _Field instances
        meta = cls_dict["_db_fields"] = dict([(k, v) for k, v in cls_dict.iteritems()
                                              if (not k.startswith("_")) and isinstance(v, _Field)])

        # Set the name field, based on the attribute name, and validate that the field is legal.
        for field_name, field in meta.items():
            field.name = field_name
            field._attributes_valid()

        # Find any primary keys which are already defined
        primaries = [name for name, field in meta.items() if field.is_primary() ]
        if not primaries:
            # No primary fields defined - so we will automatically define one - assuming no name clashes
            if "id" in cls_dict:
                raise ValueError("id field exists but is not the primary key")
            else:
                pass
                meta["id"] = AutoField()
                meta["id"].name = "id"
                cls_dict["_primary"] = mcs.meta["id"]
        else:
            if len(primaries) == 1:
                cls_dict["_primary"] = primaries[0]
            else:
                raise ValueError("More than one primary field ({names}) defined in this Model".format(
                    names = ",".join(primaries)
                ))

        #Find dependencies (i.e.tables that this maps to)
        cls_dict["_dependencies"] = [field.othermodel() for field in meta
                                     if isinstance(field,_Mapping)]

        # Create a mapping from the db_column name to the actual field - used on queries.
        cls_dict["_columns_to_attr"] = {field.db_column():field for field in meta}

        _ModelMetaClass._models[cls_name] = type.__new__(mcs, cls_name, bases, cls_dict)
        return _ModelMetaClass._models[cls_name]