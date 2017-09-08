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
from collections import OrderedDict

import pyorm.core.exceptions as exceptions
from .utils import Annotation, Related
from .functions import TruncDate

import pyorm.db.models.fields as field_defs

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '26 Aug 2017'


# Todo - Must be able to pickle everything


class F:
    """A Deferred field access - accesses the field at execution time not against the Python Model"""
    def __init__(self, field_name):
        """General class to defer field lookup until query is executed

          Can be arithmetically combined with another F object or strings
        """
        if field_name:
            self._lhs = field_name
            self._rhs = None
            self._operator = None
            self._negate = False

    @classmethod
    def CreateCombine(self, lhs=None, operator=None, rhs=None):
        """Create a combined instance"""
        c = F(lhs)
        c._rhs = rhs
        c._operator = operator
        return c

    def __eq__(self, other):
        if not isinstance(other, F):
            return False

        return self._lhs == other._lhs \
               and self._rhs == other._rhs \
               and self._operator == other._operator \
               and self._negate == other._negate

    def __hash__(self):
        return hash((repr(self)))

    def __repr__(self):
        # Repr uses () to designate the prioritisation
        # If Python builds this CombineExp first then it has the precedence
        # (either due to operator precedence or due to bracketting.
        if self._operator:
            return '{}({!r}{}{!r})'.format('-' if self._negate else '',
                                       self._lhs,
                                       self._operator, self._rhs)

        else:
            return '{}{}({})'.format('~' if self._negate else '', self.__class__.__name__, repr(self._lhs))

    def __neg__(self):
        clone = copy(self)
        clone._negate = not self._negate
        return clone

    def __pos__(self):
        clone = copy(self)
        clone._negate = False
        return clone

    def __concat__(self, other):
        return self.CreateCombine(lhs=self, operator='+', rhs=other)

    def __rconcat__(self, other):
        return self.CreateCombine(lhs=other, operator='+', rhs=self)

    def __add__(self, other):
        return self.CreateCombine(lhs=self, operator='+', rhs=other)

    def __radd__(self, other):
        return self.CreateCombine(lhs=other, operator='+', rhs=self)

    def __sub__(self, other):
        return self.CreateCombine(lhs=self, operator='-', rhs=other)

    def __rsub__(self, other):
        return self.CreateCombine(lhs=self, operator='-', rhs=other)

    def __mul__(self, other):
        return self.CreateCombine(lhs=self, operator='*', rhs=other)

    def __rmul__(self, other):
        return self.CreateCombine(lhs=self, operator='*', rhs=other)

    def __truediv__(self, other):
        return self.CreateCombine(lhs=self, operator='/', rhs=other)

    def __rtruediv__(self, other):
        return self.CreateCombine(lhs=self, operator='/', rhs=other)

    def __lshift__(self, other):
        return self.CreateCombine(lhs=self, operator='<<', rhs=other)

    def __rlshift__(self, other):
        return self.CreateCombine(lhs=self, operator='<<', rhs=other)

    def __rshift__(self, other):
        return self.CreateCombine(lhs=self, operator='>>', rhs=other)

    def __rrshift__(self, other):
        return self.CreateCombine(lhs=self, operator='>>', rhs=other)

    def __and__(self, other):
        return self.CreateCombine(lhs=self, operator='&', rhs=other)

    def __rand__(self, other):
        return self.CreateCombine(lhs=self, operator='&', rhs=other)

    def __or__(self, other):
        return self.CreateCombine(lhs=self, operator='|', rhs=other)

    def __ror__(self, other):
        return self.CreateCombine(lhs=self, operator='|', rhs=other)

    def __xor__(self, other):
        return self.CreateCombine(lhs=self, operator='^', rhs=other)

    def __rxor__(self, other):
        return self.CreateCombine(lhs=self, operator='^', rhs=other)

    def __mod__(self, other):
        return self.CreateCombine(lhs=self, operator='%', rhs=other)

    def __rmod__(self, other):
        return self.CreateCombine(lhs=self, operator='%', rhs=other)

    def resolve(self, default_alias = '',engine=None, model=None, joins=None):
        """Public method to validate an F object"""

        # If the operator and rhs elements are Non then the lhs will be field name
        # other wise one of the fields will be an F object and the other an F object or constant.
        if self._operator and self._rhs:
            try:
                lhs = self._lhs.resolve(default_alias = default_alias, engine=engine, model=model, joins=joins)
            except AttributeError:
                lhs = repr(self._lhs)
            except:
                raise

            try:
                rhs = self._rhs.resolve(default_alias = default_alias, engine=engine, model=model, joins=joins)
            except AttributeError:
                rhs = repr(self._rhs)
            except:
                raise

            return '(' + lhs + self._operator + rhs + ')'
        else:
            return engine.resolve_name(self._lhs, default_alias=default_alias, model=model, joins=joins)

class Q:
    """A class for building complex field comparisons, especially when wants to use OR combinations"""
    def __init__(self, **kwargs):
        """A Q object enables the building of potentially complex sql conditional which can be combined with & or |

        A Q object can be a combination of strings (field_lookups), or a combination of other Q objects
        """
        # Todo - there might be a need for a generalise Tree class - which this can derive from

        self._members = []

        # Any kwargs will be field lookups - and nothing else
        # Build the membership dictionary in alphabetical order
        if kwargs:
            lk = sorted([k for k in kwargs])
            self._operator = 'AND'
            self._members = [(k,kwargs[k]) for k in lk]
        else:
            self._members = []
            self._operator = None
        self._negated = False

    # noinspection PyProtectedMember
    def __and__(self, other):
        if not isinstance(other, self.__class__):
            raise exceptions.QuerySetError(
                'Cannot CreateCombine Q expression with anything else')
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
                'Cannot CreateCombine Q expression with anything else')
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
        q = self.__class__()
        q._members = self._members
        q._negated = not self._negated
        q._operator = self._operator
        return q

    def __repr__(self):
        if self._members:
            # We COULD optimise the repr in cases where members has ONE entry - but that is unlikely to matter in the long term
            return "{neg}({op} : {members})".format(
                neg=('NOT ' if self._negated else ''),
                op=self._operator,
                members=', '.join(
                    repr(term) if not isinstance(term, tuple) else term[0]+'='+repr(term[1]) for term in
                    self._members)
            )
        else:
            return ''

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise NotImplementedError
        return self._members == other._members and self._operator == other._operator and self._negated == other._negated

    def __hash__(self):
        return hash(repr(self))

    def resolve(self, default_alias = '', engine=None, model=None, joins=None):

        fs = []
        for member in self._members:
            try:
                fs.append( member.resolve( default_alias = default_alias, engine=engine, model=model, joins=joins))
            except AttributeError:
                fs.append( engine.resolve_lookup(*member,default_alias = default_alias, model=model,joins=joins))
            except:
                raise

        return '{negated}({fields})'.format(
                                negated='NOT ' if self._negated else '',
                                fields = (' ' +self._operator+' ').join(fs) )

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
    """ A Base class for any query which can be ordered and limited

        The base for the SimpleQuery and Combination query types
    """
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

    def set_limits(self, *limits):
        """Set the limits"""
        if len(limits) >2:
            raise exceptions.LimitsError
        self._limits = [*limits]

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
        self._criteria = criteria if criteria else Q()

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
        self._qs = [*qs] if qs else []

    @property
    def queries(self):
        return self._qs


class Union(Combination):
    """A class for recording a UNION query"""
    def __init__(self, *qs, order_by=None, get_all=False):
        super().__init__(*qs, order_by=order_by)
        self._get_all = get_all

    @property
    def get_all(self):
        return self._get_all

class Intersection(Combination):
    """A class for recording an INTERSECT query"""
    def __init__(self, *qs, order_by=None):
        super().__init__(*qs, order_by=order_by)


class Difference(Combination):
    """A class for recording an EXCEPT query"""
    def __init__(self, *qs, order_by=None):
        super().__init__(*qs, order_by=order_by)

class Join:
    """Class for Join information - holds a tree of join Nodes"""
    class Node:
        """A class defining the linkage between a model and it's parent

          Each Node defines how a given relation connects a model to the parent
        """
        def __init__(self, parent=None, relation_name='', model=None, fields=(), allow_nulls=False):
            """Build a node, which defines the relationship between two models

            :param parent: The parent node of this join node
            :param relation_name: The name of the relation from the parent model
            :param model: The model that this node relates to
            :param fields:  The fields that define this relationship
                            a 2-tuple : (parent field, child_field)
            :param allow_nulls: Whether this side of the relationship can be null.

            Example:

            With two models A & B forms a relationship named 'foo' where the two
            models are connected by the criteria A.foo_bar = B.bar_foo

            parent = the Node that defines A
            relation_name = 'foo'
            model = B
            fields = ('foo_bar', 'bar_foo')
            allow_nulls = True if entries from model B can be omitted
            """
            self._model = model
            self._parent = parent
            self._relation = relation_name
            self._fields = fields
            self._children = OrderedDict()
            self._allow_nulls = allow_nulls

        def __repr__(self):
            if self._parent:
                return 'Join {alias}: {parentTable} => {table} {parentTable}.{parent_field}={table}.{table_field}'.format(
                        alias = self.relation,
                        parentTable = self._parent.model.table_name(),
                        table = self._model.table_name(),
                        parent_field = self._fields[0],
                        table_field = self._fields[1]
                        )
            else:
                return '{alias}: {table}'.format(
                        alias = self.relation,
                        table = self._model.table_name(),
                        )

        def __hash__(self):
            return hash(repr(self))

        def __eq__(self, other):
            return repr(self) == repr(other)

        @property
        def allow_nulls(self):
            return self._allow_nulls

        @property
        def parent(self):
            """The parent node of this node - could be None"""
            return self._parent

        @property
        def model(self):
            """The mode for this node - i.e. the rhs of the relationship"""
            return self._model

        @property
        def relation(self):
            """The name of the relationship - this will be a relation on the parent model"""
            return self._relation

        @relation.setter
        def relation(self, value):
            """Allow setting of the relation name"""
            self._relation = value

        @property
        def fields(self):
            """The fields that define the connection between the two models"""
            return self._fields

        @property
        def children(self):
            """The child nodes of this model/relation"""
            return self._children

    def __init__(self, root_model=None, sep='__'):
        """Create an initial Join onto a single table"""
        self._root = self.Node(parent=None, relation_name='', model=root_model, fields=())
        self._sep = sep
        self._index = {}

    def from_tuple(self, joins):
        """Build a simple set of joins based a provided set of tuples

          Provides a way to create joins which aren't dependent on existing relations

         :param joins: an interable of tuples
                The tuples 5-tuples:
                (Model class, alias str, parent alias, field name on parent, field name on model, allow_nulls)
        """
        if self._root.children:
            raise exceptions.JoinError('Cannot use from_tuple to add to existing joins')

        if not self._root.relation:
            self._root.relation = self._root.model.table_name()
            self._root._relation_path = [self._root.model.table_name()]

        for a_join in joins:
            try:
                model,alias,parent_alias,parent_field,field_name,allow_nulls = a_join
            except ValueError:
                raise exceptions.JoinError('Unexpected format of tuple - expecting 6 elements')

            parent_node = self._find_relation(parent_alias)
            if not parent_node:
                if not (parent_alias == self._root.relation):
                    raise exceptions.JoinError('Parent alias \'{}\' does not exist'.format(parent_alias))
                else:
                    parent_node = self._root

            node = self.Node(parent=parent_node, relation_name=alias,
                             model=model,
                             fields=(parent_field, field_name),
                             allow_nulls=allow_nulls)
            parent_node.children[alias] = node
            self._index[alias] = node


    def _find_deepest_parent(self, full_relation_name):
        """Find the deepest existing parent for this  given relation name within the current node tree

        :param full_relation_name
        :return: Either the Node
        """
        parent_name = self._sep.join(full_relation_name.split(self._sep)[:-1])
        while parent_name and not self._index.get(parent_name, None):
            parent_name = self._sep.join(parent_name.split(self._sep)[:-1])

        return self._index[parent_name] if parent_name else self._root

    def _find_relation(self, full_relation_name):
        """Find a given relation name within the current node tree

        :param full_relation_name: The name with components separated by '__'
        :return: Either the Node or None
        """
        return self._index.get(full_relation_name,None)

    def _addNode_to_parent(self, element='', parent=None, allow_nulls=False):
        """Add a node to the Parent node

        :param element: The relevant component of the relation name
        :param parent: The parent node
        :return:

        Creates an Node instance, adds it to the children of the parent
        and add the full path to the index

        """
        relation_info = parent.model.get_relationship(element)
        related_model, field, related_field = relation_info
        node = self.Node(parent=parent, relation_name=parent.relation + self._sep + element,
                         model=related_model,
                         fields=(field, related_field),
                         allow_nulls=allow_nulls)
        parent.children[element] = node
        self._index[parent.relation + self._sep + element] = node
        return node

    def _create_path(self, relation_name, allow_nulls=False):
        """Create a path to the relation_name building nodes as we go"""

        # Find the deepest parent node for this relation
        parent = self._find_deepest_parent(relation_name)

        # Identify what is missing
        remaining_elements = relation_name.split(self._sep)[len(parent._relation_path) - 1:]

        # Build out what is missing, if anything
        if remaining_elements:
            for element in remaining_elements:
                node = self._addNode_to_parent(element=element, parent=parent, allow_nulls=allow_nulls)
                parent = node
            return node
        else:
            return parent

    def addJoin(self, model_path, allow_nulls=False):
        """Public method to add a join - based on a relation to the initial model"""
        if not self._root.relation:
            self._root.relation = self._root.model.table_name()
            self._root._relation_path = [self._root.model.table_name()]

        node = self._find_relation(model_path)
        if not node:
            return self._create_path(model_path,allow_nulls=allow_nulls)
        else:
            return node

    def _flatten(self, parent_node=None, sep=None):
        """Convert the tree into a depth first iteratable"""

        parent_node = parent_node if parent_node else self._root
        sep = sep if sep else self._sep

        yield (parent_node.relation, parent_node)

        for relation, node in parent_node.children.items():
            if node._children:
                yield from self._flatten(parent_node=node, sep=sep)
            else:
                yield (node.relation, node)
        else:
            return

    def items(self):
        """Public iterator method"""
        yield from self._flatten()

    def to_sql(self):
        """Create """
        sql = ''
        for path, node in self._flatten():
            if not node.parent:
                sql += "{} {}\n".format(node.model.table_name(),node.relation)
            else:
                outer = node._allow_nulls and not node.children
                sql += 'LEFT {outer} JOIN {table_name} {node.relation} ON {parent.relation}.{fields[0]} = {node.relation}.{fields[1]}\n'.format(
                    outer='OUTER' if outer else '',
                    table_name = node.model.table_name(),
                    node = node,
                    parent = node.parent,
                    fields= node.fields)

        return sql


class SimpleQuery(FilterableQuery):
    """A simple SQL query - i.e. not a Compound Query or a pre-built SQL Query"""
    def __init__(self, options=None, joins=None,fields=None,criteria=None, order_by = None):
        super().__init__()
        self._options = options if options else []
        self._fields = fields if fields else []
        self._joins = joins if joins else []
        self._criteria = criteria if credits else []
        self.add_order_by(order_by if order_by else [])

    @property
    def options(self):
        return self._options

    @property
    def fields(self):
        return self._fields

    @property
    def joins(self):
        return self._joins

    @property
    def criteria(self):
        return self._criteria

    @classmethod
    def from_model(cls, model=None, order_by=None):
        """Class factory method to build a Query Set based on an existing model"""
        if not model:
            return
        inst = cls(joins=[Join(TableInfo(table_name=model, field=model.primary_field(), alias=model.table_name()), None)],
                   fields =  [definition.db_column for name, definition in model.db_fields()],
                   order_by = order_by if order_by else model.order_by())
        return inst

    def add_options(self, *options):
        """Add items to the options list"""
        self._options += [*options]

    def add_joins(self, *joins):
        """Add tables to the tables list"""
        self._joins += [*joins]

    def clear_joins(self):
        """Clear the table list"""
        self._joins = []

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
