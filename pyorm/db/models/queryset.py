#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of queryset.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
from copy import copy
import pyorm.core.exceptions as exceptions
from .utils import Annotation, Related
from .functions import TruncDate

import pyorm.db.models.fields as field_defs

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '26 Aug 2017'


# Todo - Must be able to pickle everything


def magic_method_wrapper(operator, name):
    """Wrapper Used to add magic Methods to the CombinedExp class"""

    def __method__(self, other):
        return CombinedExp(lhs=self, operator=operator, rhs=other)

    __method__.__name__ = name
    return __method__


def add_operators(cls):
    """Decorator to add appropriate operator magic methods"""
    ops = {'+': ('__add__', '__radd__'),
           '-': {'__sub__', '__rsub'},
           '*': ('__mul__', '__rmul__'),
           '/': {'__truediv__', '__rtruediv__'},
           '<<': {'__lshift__', '__rlshift__'},
           '>>': {'__rshift__', '__rrshift__'},
           '^': {'__xor__', '__rxor__'},
           '&': {'__and__', '__rand__'},
           '|': {'__or__', '__ror__'},
           '%': {'__mod__', '__rmod__'}
           }
    for op, names in ops.items():
        for name in names:
            setattr(cls, name, magic_method_wrapper(op, name))
    return cls


@add_operators
class F:
    """A Deferred field access - accesses the field at execution time not against the Python Model"""
    def __init__(self, field_name):
        """General class to defer field lookup until query is executed

          Can be arithmetically combined with aother
        """
        self._field_name = field_name
        self._negate = False

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __hash__(self):
        return hash((repr(self)))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self._field_name))

    def __neg__(self):
        self._negate = not self._negate
        return self

    def __pos__(self):
        self._negate = False
        return self


class CombinedExp(F):
    """An Expression for F objects

    A binary operator where at least one operand is an F object

    Relies on Python identifying operator precedence.

    With Complex operations this will form an effective tree of objects

    Object will have no knowledge of where it is in the tree
    """
    def __init__(self, lhs, operator, rhs):
        super().__init__('')
        self._lhs = lhs
        self._operator = operator
        self._rhs = rhs
        self._negate = False

    def __repr__(self):
        # Repr uses () to designate the prioritisation
        # If Python builds this CombineExp first then it has the precedence
        # (either due to operator precedence or due to bracketting.
        return '{}({!r}{}{!r})'.format('-' if self._negate else '', self._lhs,
                                       self._operator, self._rhs)

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return repr(self) == repr(other)


class Q:
    """A class for building complex field comparisons, especially when wants to use OR combinations"""
    def __init__(self, **kwargs):
        """A Q object enables the building of potentially complex sql conditional which can be combined with & or |

        A Q object can be a combination of strings (field_lookups), or a combination of other Q objects
        """
        # Todo - there might be a need for a generalise Tree class - which this can derive from

        self._members = []

        # Any kwargs will be field lookups - and nothing else
        if kwargs:
            lk = sorted([k for k in kwargs])
            self._operator = 'AND'
            self._members = ['{}={}'.format(k, repr(kwargs[k])) for k in lk]
        else:
            self._member = []
            self._operator = None
        self._negated = False

    # noinspection PyProtectedMember
    def __and__(self, other):
        if not isinstance(other, self.__class__):
            raise exceptions.QuerySetError(
                'Cannot combine Q expression with anything else')
        q = self.__class__()
        # Doing an & with an empty Q is a simple copy
        if self._members and other._members:
            q._combine(self, other)
        else:
            q._members = self._members if self._members else other._members
            q._operator = self._operator if self._operator else other._operator

        return q

    # noinspection PyProtectedMember
    def __or__(self, other):
        if not isinstance(other, self.__class__):
            raise exceptions.QuerySetError(
                'Cannot combine Q expression with anything else')
        q = self.__class__()

        # Doing an | with an empty Q is a simple copy
        if self._members and other._members:
            q._combine(self, other, operator='OR')
        else:
            q._members = self._members if self._members else other._members
            q._operator = self._operator if self._operator else other._operator

        return q

    def _combine(self, *members, operator='AND'):
        self._members = [*members]
        self._operator = operator

    def __invert__(self):
        self._negated = not self._negated
        return self

    def __repr__(self):
        if self._members:
            # We COULD optimise the repr in cases where members has ONE entry - but that is unlikely to matter in the long term
            return "{neg}({op} : {members})".format(
                neg=('NOT ' if self._negated else ''),
                op=self._operator,
                members=', '.join(
                    repr(x) if not isinstance(x, str) else x for x in
                    self._members)
            )
        else:
            return ''

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise NotImplemented
        return repr(self) == repr(other)


class BaseQuery:
    """Common class for ALL queries

        record capabilities of the superclass without resorting to checking class types
    """
    def __init__(self, mutable=True, extendable=True, filterable=True,
                 orderable=True, limitable=True):
        self._mutable = mutable
        self._extendable = extendable and mutable
        self._filterable = filterable and mutable
        self._orderable = orderable and mutable
        self._limitable = limitable and mutable

    @property
    def is_mutable(self):
        """Is this query changable"""
        return self._mutable

    @property
    def is_extendable(self):
        """Is this query extendable - can the fields be changed"""
        return self._extendable

    @property
    def is_filterable(self):
        """Is this query filterable - can the WHERE clause change"""
        return self._filterable

    @property
    def is_orderable(self):
        """Is this query orderable - can the ORDER BY clause change"""
        return self._orderable

    @property
    def is_limitable(self):
        """Is this query limitable - can the quaery be given a LIMIT clause"""
        return self._limitable


class OrderingAndLimits(BaseQuery):
    """ A Base class for any query which can be ordered and limited """
    def __init__(self, order_by=None, limits=None, filterable=True,
                 extendable=True, limitable=True):
        super().__init__(orderable=True, limitable=limitable, filterable=filterable,
                         extendable=extendable)
        self._order_by = order_by if order_by else []
        self._limits = limits if limits else []

    def add_order_by(self, *order_bys):
        """Add a field or ordinal to the Order by list"""
        self._order_by += [*order_bys]

    def clear_order_by(self):
        """Clear the Order by list"""
        self._order_by = []

    def invert_ordering(self):
        """Reverse the Order by list"""
        self._order_by = [self.invert_item(o) for o in self._order_by]

    @staticmethod
    def invert_item(o):
        """Invert a specific item within the Order by List"""
        if isinstance(o, str):
            return o[1:] if o[0] == '-' else '-' + o
        else:
            return -o

    @property
    def order_by(self):
        """Expose the order by list"""
        return self._order_by

    def add_limits(self, *limits):
        """Add a limits to the limit list"""
        if len(limits) > 2:
            raise exceptions.LimitsError
        self._limits += [*limits]

    def clear_limits(self):
        """Clear the limit list"""
        self._limits = []

    @property
    def limits(self):
        """Expose the limit list"""
        return self._limits


class FilterableQuery(OrderingAndLimits):
    """A General class for any query which can be filtered"""
    def __init__(self, criteria=None, order_by=None, limitable=True):
        """A General class for any query which can be filtered

          Filters stored as a Q object (which could be a tree)
        """
        super().__init__(filterable=True, limitable=limitable, order_by=order_by)
        if criteria:
            assert isinstance(criteria, Q)
        self._criteria = criteria

    @property
    def criteria(self):
        """Expose the criteria attribute"""
        return self._criteria

    @criteria.setter
    def criteria(self, value):
        """Expose the criteria attribute to be set"""
        self._criteria = value


class RawSQL(BaseQuery):
    """A Special Query object which is defined by SQL only - so immutable"""
    def __init__(self, sql, parameters):
        """A Query defined by an existing and complete SQL query

           Cannot be modified any futher
        """
        super().__init__(mutable=False)
        self._sql = sql
        self._paramters = parameters


class Combination(OrderingAndLimits):
    """A Generic class for Queries which are compound Queries"""
    def __init__(self, *qs, order_by=None):
        super().__init__(order_by, filterable=False, extendable=False)
        self._qs = qs


class Union(Combination):
    """A class for recording a UNION query"""
    def __init__(self, *qs, order_by=None, get_all=False):
        super().__init__(*qs, order_by)
        self._get_all = get_all


class Intersection(Combination):
    """A class for recording an INTERSECT query"""
    def __init__(self, *qs, order_by=None):
        super().__init__(*qs, order_by)


class Difference(Combination):
    """A class for recording an EXCEPT query"""
    def __init__(self, *qs, order_by=None):
        super().__init__(*qs, order_by)


class SimpleQuery(FilterableQuery):
    """A simple SQL query - i.e. not a Compound Query or a pre-built SQL Query"""
    def __init__(self):
        super().__init__()
        self._options = []
        self._tables = []
        self._fields = []
        self._joins = []

    def add_fields_from_model(self, model):
        """Given an existing model - build a field list for the model"""
        self.clear_fields()
        self.add_fields(tuple(
            definition.db_column for name, definition in model.db_fields()))

    @classmethod
    def from_model(cls, model=None, order_by=None):
        """Class factory method to build a Query Set based on an existing model"""
        if not model:
            return
        inst = cls()
        inst.add_table((model.table_name(), model.table_name()))
        inst.add_fields_from_model(model.db_fields())
        inst.add_order_by(*order_by if order_by else 'id')

    def add_options(self, *options):
        """Add items to the options list"""
        self._options += [*options]

    def add_table(self, *tables):
        """Add tables to the tables list"""
        self._tables += [*tables]

    def clear_tables(self):
        """Clear the table list"""
        self._tables = []

    def add_fields(self, *new_fields):
        """Add fields to the fields list"""
        self._fields += [*new_fields]

    def clear_fields(self):
        """Clear the fields list"""
        self._fields = []


# noinspection PyMethodMayBeStatic
class Cache:
    """A class which will support Caching for Query results - and prefetching"""
    def __init__(self, cache_id, model):
        self._id = id
        self._id = model


class QuerySet(object):
    """A Class designed to allow simple building of complex queries"""
    def __init__(self, model=None, query=None, order_by=None):
        """
        A generalised query object for a given object - allows the construction of filters
        """

        self._model = model
        self._query = query if query else (
            SimpleQuery.from_model(model, order_by=order_by) if model else None)
        self._related = []
        self._defered = []
        self._output = 'models'
        self._cache = self._cache.get_cache_instance(id(self))

    @property
    def query(self):
        """Query property - expose the Query used to build this set"""
        return self._query

    @query.setter
    def query(self, value):
        """Allow external setting of the query attribute"""
        self._query = value

    def _clone(self):
        """Take a copy of this clone"""
        return copy(self)

    def _criteria_add(self, exclude=False, **kwargs):
        """AND a Q object into the criteria list - with a possible negation"""
        if exclude:
            self._query.criteria &= ~Q(**kwargs)
        else:
            self._query.criteria &= Q(**kwargs)

    def filter(self, **kwargs):
        """Add these filters to the query criteria - they ANDed to any existing criteria"""
        if not self.query.is_filterable:
            raise exceptions.NotModfiable
        clone = self._clone()
        clone._criteria_add(exclude=False, **kwargs)
        return clone

    def exclude(self, **kwargs):
        """Add these filters to the query criteria - they AND to any existing criteria with negation"""
        if not self._query.is_filterable:
            raise exceptions.NotModfiable
        clone = self._clone()
        clone._criteria_add(exclude=True, **kwargs)
        return clone

    def annotate(self, *args, **kwargs):
        """Add an extra field (which may well be an aggregate)"""
        if not self._query.is_extenable:
            raise exceptions.NotModfiable
        clone = self._clone()
        clone.query.add_fields(Annotation(*args, **kwargs))
        return clone

    def order_by(self, *args):
        """Add fields or orderables to the order by attribute - if none given ordering is cleared"""
        if not self._query.is_orderable:
            raise exceptions.NotModfiable
        clone = self._clone()
        if args:
            clone.query.add_orderby(tuple([p for p in args]))
        else:
            clone.query.clear_orderby()
        return clone

    def reverse(self):
        """Invert the ordering of the query"""
        if not self._query.is_orderable:
            raise exceptions.NotModfiable
        clone = self._clone()
        clone.query.invert_order_by()
        return clone

    def distinct(self):
        """Make this query DISTINCT"""
        if not self._query.is_mutable:
            raise exceptions.NotModfiable
        clone = self._clone()
        clone.query.add_options('DISTINCT')
        return clone

    def values(self, *names):
        """Change this query so the the results are returned as a dictionary"""
        if not self._query.is_extendable:
            raise exceptions.NotModfiable
        clone = self._clone()
        clone._output = 'dict'
        if names:
            clone.query.add_fields(*names)
        else:
            clone.query.add_fields_from_model(clone._model)
        return clone

    def values_list(self, *names, flat=False):
        """Change this query so the named fields are returned as tuples in a list

           A result set of a single field can be returned as a flat array
        """
        if not self._query.is_extendable:
            raise exceptions.NotModfiable

        if names and len(names) > 1 and flat:
            raise AttributeError('Cannot flatten a multi field query')

        clone = self._clone()
        clone._output = 'list' if flat else 'flat-list'
        if names:
            clone.query.add_fields(*names)
        else:
            clone.query.add_fields_from_model(clone._model)
        return clone

    # Todo - Dates and Datetime Truncation might return a string - need to ensure Date/DateTimeFields accept ISO standard fields
    def dates(self, field, kind, order='ASC'):
        """Produce a UNIQUE list of date files which are truncated to the appropriate kind

           kind is one of 'years', 'months', 'days'
        """
        if not self._query.is_extendable:
            raise exceptions.NotModfiable

        if kind.lower() not in ['years', 'months', 'days']:
            raise AttributeError('Invalid truncation option {}'.format(kind))
        clone = self._clone()
        clone.query.clear_fields()
        clone.query.add_fields(
            Annotation(TruncDate(field, kind), alias=field + '_' + kind,
                       dataType=field_defs.DateField(), order=order))
        return clone

    def datetimes(self, field, kind, order='ASC', tzinfo=None):
        """Produce a UNIQUE list of date files which are truncated to the appropriate kind

           kind is one of 'years', 'months', 'days', 'hours', 'minutes', 'seconds'
        """
        if not self._query.is_extendable:
            raise exceptions.NotModfiable

        if kind.lower() not in ['years', 'months', 'days', 'hours', 'minutes',
                                'seconds']:
            raise AttributeError('Invalid truncation option {}'.format(kind))
        clone = self._clone()
        clone.query.clear_fields()
        clone.query.add_fields(
            Annotation(TruncDate(field, kind), alias=field + '_' + kind,
                       dataType=field_defs.DateTimeField(), order=order, tz=tzinfo))
        return clone

    def none(self):
        """Return a new Query Set which is empty - not even a model"""
        return self.__class__()

    def all(self):
        """Create a copy of the Query set."""
        return self._clone()

    # noinspection PyShadowingBuiltins
    def union(self, *qs, all=True):
        """Build a UNION query from this Query and the others"""
        clone = self._clone()
        clone.query = Union(self._query, tuple(q.query for q in qs),
                            get_all=all)
        return clone

    def intersect(self, *qs):
        """Build a INTERSECT query from this Query and the others"""
        clone = self._clone()
        clone.query = Intersection(self._query, tuple(q.query for q in qs))
        return clone

    def difference(self, *qs):
        """Build a EXCEPT query from this Query and the others"""
        clone = self._clone()
        clone.query = Difference(self._query, tuple(q.query for q in qs))
        return clone

    def select_related(self, *fields):
        """Select some more fields in this query"""
        clone = self._clone()

        if not fields or fields[0] is None:
            clone._related = []
        else:
            clone._related += [Annotation(Related(*fields))]

        return clone
        # Todo - Need to add hooks into managers/model fields for the new models to point back to the caches

    def prefetch_related(self, *lookups):
        """Prefetch some data to reduce DB hits"""
        clone = self._clone()
        return clone
        # Todo Prefetching of related items - need a design
        # Todo - Need to add hooks into managers/model fields for the new models to point back to the caches

    def defer(self, *fields):
        """Defer the fetching of specific fields"""
        clone = self._clone()
        clone._defered += [*fields]
        return clone
        # Todo Defer fetching of items

    def only(self, *fields):
        """Limit the fetching to some fields"""
        if not self._query.is_extendable:
            raise exceptions.NotModfiable
        clone = self._clone()
        clone.query.clear_fields()
        clone.query.add_fields(*fields)
        clone.query.clear_order_by()
        return clone
        # Todo Only fetch some fields fetching of items

    def select_for_update(self):
        """Fetch a set of data which will be locked for updates"""
        clone = self._clone()
        return clone
        # Todo change query

    def raw(self, sql, params):
        """Make this Query Set a RAW Query set - everything else will be reset"""
        clone = self.__class__(query=RawSQL(sql, params))
        return clone

    #
    #  Methods that don't return a QuerySet
    #

    # ToDo - WHat the hell does this do ????
    # noinspection PyMethodMayBeStatic
    def _transform(self, obj):
        """Chnage the output to the relevant output format - model, dict, list, list-flat"""
        return obj

    def get(self, **kwargs):
        """Try to get a single model from this query set"""
        qs = self.filter(**kwargs)
        cache_inst = self._cache.get_cache_instance(id(self), model=self._model)
        qs.query.execute(cache_inst)

        if len(cache_inst) == 0:
            raise exceptions.DoesNotExist

        if len(cache_inst) > 1:
            raise exceptions.MultipleObjects

        return self._transform(cache_inst[0])
