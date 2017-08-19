# /usr/bin/env python
#
# DBmodels : Test Suite for model
# 
# <Module Summary statement>
#

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '23 Sep 2014'

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

from ._core import _Field, _Mapping, _ModelMetaClass

from pyorm.core.exceptions import InvalidField, UnknownCondition

class ManyToMany(_Mapping, _Field, ):
    pass


class QuerySet(object):
    conditions = ["eq", "lt", "gt", "lte", "gte", "contains", "startswith", "endswith", "like", "ilike", "in"]

    def __init__(self, model):
        """
        A generalised query object for a given object - allows the construction of filters
        """
        self._model = model
        self._clause = []

        self._eq = lambda field, value: self._cmp(field, value, "=")
        self._lt = lambda field, value: self._cmp(field, value, "<")
        self._gt = lambda field, value: self._cmp(field, value, ">")
        self._lte = lambda field, value: self._cmp(field, value, "<=")
        self._gte = lambda field, value: self._cmp(field, value, ">=")
        self._contains = lambda field, value: self._cmp(field, "'%" + repr(value) + "%'", "LIKE")
        self._startswith = lambda field, value: self._cmp(field, repr(value) + "%'", "LIKE")
        self._endswith = lambda field, value: self._cmp(field, "'%" + repr(value) + "%'", "LIKE")
        self._in = lambda field, value: self._cmp(field, value, "IN")

    def _cmp(self, field, value, cmp_op):
        db_field = self._model.db_fields()[field].db_column()

        # Compare to NULL/None correctly
        if repr(value) is None and cmp_op == "=":
            return "{0} is NULL"

        # If the value is another query set, then make sure it is enclosed in braces
        if isinstance(value, QuerySet):
            return "{0} {1} ({2})".format(db_field, cmp_op, repr(value))

        return "{0} {1} {2}".format(db_field, cmp_op, repr(value))

    def _construct_clause(self, criteria):
        for clause, value in criteria.iteritems():
            clause_split = clause.split("__")
            field = clause_split[0]
            condition = clause_split[1] if len(clause_split) == 2 else "eq"

            if field not in self._model.db_fields():
                raise InvalidField("Invalid field {0}".format(field))

            if condition not in QuerySet.conditions:
                raise UnknownCondition("Query Set condition {0} unkown".format(condition))
            yield self.__getattribute__("_" + condition)(field, value)

    def all(self):
        """ Lazy evaluation of a SELECT * from table"""
        table = self._model.__table__
        self._clause = {"True": "True"}

    def get(self, **kwargs):
        """Build query, based on the kwargs - Immediate execution"""
        self._clause = " AND ".join([clause for clause in self._construct_clause(**kwargs)])

    def filter(self, **kwargs):
        """Filters the data in a query set - lazy evaluation"""
        self._clause = " AND ".join([clause for clause in self._construct_clause(**kwargs)])

    def exclude(self, **kwargs):
        self._clause = "NOT (" + " AND ".join([clause for clause in self._construct_clause(**kwargs)]) + ")"

    def __repr__(self):
        return "SELECT {cols} FROM {table} WHERE {clause}".format(
            cols=",".join([meta.db_column for col, meta in self._model.db_fields().iteritems()]),
            table=self._model.__table__,
            clause=self._clause
        )


class Model(object):
    __metaclass__ = _ModelMetaClass

    def __new__(cls, *args, **kwargs):
        cls.objects = QuerySet(cls)
        return super(Model, cls).type(cls, *args, **kwargs)

    def __init__(self, **kwargs):
        super(Model, self).__init__()

        # Set defined fields as instance attributes - use kwargs to set values or use defaults
        for name, field in Model.db_fields().iteritems():
            if field.is_mutable and (name in kwargs):
                raise AttributeError("Cannot set value of AutoField '{name}'".format(name=name))
            super(Model, self).__setattr__(name, kwargs.get(name, field.default))
        self._save_cmd = "INSERT"

    @classmethod
    def instance_from_query(cls, cls_name, **kwargs):
        instance = Model._models[cls_name](**kwargs)
        instance._save_cmd = "UPDATE"
        return instance

    @classmethod
    def _create_table_sql(cls):
        """Returns the creation sql for this model"""
        # ToDo - Doesn't deal with dependencies between models
        sql = "CREATE TABLE IF NOT EXISTS {table} ".format(table=cls.__table__)
        cols = [inst._create_table_sql() for name, inst in cls.db_fields().iteritems()]
        return sql + "(\n\t" + ",\n\t".join(cols) + ")"

    @classmethod
    def _create_index_sql(cls):
        """Returns a set of strings representing the indexes for this model"""
        cols = [inst._create_index_sql() for name, inst in cls.db_fields().iteritems()]
        return "\n".join(cols)

    @classmethod
    def primary_name(cls):
        """Returns the primary key for this instance - this is a _Field instance - not a raw value

        :rtype : _FieldABC instance (i.e. a subclass of _FieldABC or _Field
        """
        return cls._primary

    @classmethod
    def primary_field(cls):
        return cls.db_fields()[cls._primary]

    @classmethod
    def dependencies(cls):
        """  Return a list of the Models which this model is dependent on
        """
        return cls._dependencies

    @classmethod
    def objects(cls):
        """do a basic query against the database

          Will return a query object - with some key methods
        """
        return cls.objects

    def __setattr__(self, key, value):

        # Set the value - including extra validation if this is a database field
        if key not in Model.db_fields():
            super(Model, self).__setattr__(key, value)

        meta = Model.db_fields()[key]
        super(Model, self).__setattr__(key, meta._check_value(new_value=value,
                                                              old_value=super(Model, self).__getattribute__(key)))

    @classmethod
    def db_fields(cls):
        return cls._db_fields

    @classmethod
    def which_attr(cls, db_column):
        """Look up to translate a specific db_column name into the attribute name"""
        return cls._columns_to_attr[db_column].name
