#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Test Suite for test_queryset.py

Summary : 
    <summary of module/class being tested>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>

Test Suites:
    500 - Field Lookups <table/relation>_<field>__<test>=<value> #ToDo
    510 - Q objects
    520 - F objects 
    530 - Query Hierarchy & TableInfo & Join classes
    540 - Query
    550 - Query Sets
    
"""

# Todo Tests 500, 520, 530,540,550,560
import sys

import unittest
import click
import inspect
from collections import Counter
from functools import partial

from unittest.mock import MagicMock, Mock, call, sentinel

from pyorm.db.models.queryset import F, Q, BaseQuery, OrderingAndLimits, \
    QuerySet, FilterableQuery, RawSQL, Combination, Difference, Union, \
    Intersection, Join, SimpleQuery

from pyorm.db.engine.core import EngineCore
from pyorm.db.models.models import Model
import pyorm.db.models.fields as fields
import pyorm.core.exceptions as exceptions

from pyorm.db.models.utils import Annotation
from pyorm.db.models.aggregates import Count, Sum, Avg, Max, Min

from tests.DummyEngine import DummyEngine, MockedEngine
import decimal
import datetime

from copy import copy

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '27 Aug 2017'


class Invariant:
    """Context Manager to ensure that object or objects don't change in the scope"""

    def __init__(self, *objs):
        """Conext manager to confirm that an object doesn't change within that context

           Confirms that the each attribute is bound to the same value or to a object which tests equal
           this is a shallow comparison only - it doesn't test attributes of attrributes.
        """
        self._objs = list(objs)
        self._old_objs = [copy(obj) for obj in self._objs]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            return False
        for index, (obj, old_obj) in enumerate(
                zip(self._objs, self._old_objs)):
            for att in obj.__dict__:
                if getattr(obj, att) == getattr(old_obj, att):
                    continue
                else:
                    raise ValueError(
                        '\'{name}\' attribute is different on object index {index}: \noriginal : {original!r}\n     now : {now!r}'.format(
                            name=att, now=getattr(obj, att),
                            index=index,
                            original=getattr(old_obj, att))) from None


# ToDo Test Looks generate the right SQL and tables

class TestQ(unittest.TestCase):
    """Test Q objects -

    Q instance are the building blocks of filterable queries
    """

    # noinspection PyMissingOrEmptyDocstring
    def setUp(self):
        pass

    def test_510_000_empty_Q(self):
        """Create an entry Q object, and prove it is really empty"""
        q = Q()
        self.assertEqual(q, Q())
        self.assertEqual(q._members, [])
        self.assertIsNone(q._operator)
        self.assertFalse(q._negated)

    def test_510_001_simpleQ(self):
        """Test for the creation of a simple Q class with a simple keyword"""

        # Q objects And their comparisons together by default
        q = Q(table_field__lte=17)
        self.assertNotEqual(q, Q())
        self.assertEqual(repr(q), '(AND : table_field__lte=17)')

        # Test that Attrributes are set as expected
        self.assertEqual(q._operator, 'AND')
        self.assertEqual([k for k in q._members], [('table_field__lte', 17)])
        self.assertFalse(q._negated)

    def test_510_002_empty_Q_and(self):
        """Test that we can And a completed and empty Q object together : Empty & Q"""
        q = Q()
        with Invariant(q):
            q1 = q & Q(test_name=17)

        self.assertNotEqual(q1, Q())
        self.assertEqual(q1, Q(test_name=17))

        self.assertEqual(q1._operator, 'AND')
        self.assertEqual([k for k in q1._members], [('test_name', 17)])
        self.assertFalse(q._negated)

    def test_510_003_empty_Q_or(self):
        """Test that we can Or a completed and empty Q object together : Empty | Q"""
        q = Q()

        with Invariant(q):
            q1 = q & Q(test_name=17)

        self.assertNotEqual(q1, Q())
        self.assertEqual(q1, Q(test_name=17))

        # OR with an Empty Set is effectively a copy.
        self.assertEqual(q1._operator, 'AND')
        self.assertEqual([k for k in q1._members], [('test_name', 17)])
        self.assertFalse(q._negated)

    def test_510_004_empty_Q_and(self):
        """Test that we can And a completed and empty Q object together : Q & Empty"""
        q = Q()
        with Invariant(q):
            q1 = Q(test_name=17) & q

        self.assertNotEqual(q1, Q())
        self.assertEqual(q1, Q(test_name=17))

        self.assertEqual(q1._operator, 'AND')
        self.assertEqual([(k, v) for k, v in q1._members], [('test_name', 17)])
        self.assertFalse(q._negated)

    def test_510_005_empty_Q_or(self):
        """Test that we can And a completed and empty Q object together : Q | Empty"""
        q = Q()
        with Invariant(q):
            q1 = Q(test_name=17) | q

        self.assertNotEqual(q1, Q())
        self.assertEqual(q1, Q(test_name=17))

        # OR with an Empty Set is effectively a copy.
        self.assertEqual(q1._operator, 'AND')
        self.assertEqual([(k, v) for k, v in q1._members], [('test_name', 17)])
        self.assertFalse(q._negated)

    def test_510_007_negated_simpleQ(self):
        """Test a negated Q class"""
        q = Q(table_field__lte=17)
        with Invariant(q):
            q1 = ~q

        self.assertEqual(repr(q1), 'NOT (AND : table_field__lte=17)')
        self.assertEqual(q1._operator, 'AND')
        self.assertEqual([(k, v) for k, v in q1._members],
                         [('table_field__lte', 17)])
        self.assertTrue(q1._negated)

    def test_510_103_two_argumentQ(self):
        """Test creation of a Q instance with multiple keyword arguments"""
        q = Q(table_field__lte=17, table_section_gte=23)

        # A Q object with multiple keyword arguments are anded together
        self.assertEqual([(k, v) for k, v in q._members],
                         [('table_field__lte', 17), ('table_section_gte', 23)])
        self.assertEqual(q._operator, 'AND')
        self.assertFalse(q._negated)

    def test_510_104_two_argumentQ_string(self):
        """Test creation of a Q instance with multiple keyword arguments - with one string value"""
        q = Q(table_field__iexact='hello', table_section_gte=23)

        # A Q object with multiple keyword arguments are anded together
        self.assertEqual([(k, v) for k, v in q._members],
                         [('table_field__iexact', 'hello'),
                          ('table_section_gte', 23)])
        self.assertEqual(q._operator, 'AND')
        self.assertFalse(q._negated)

    def test_510_105_two_argumentQ_decimal(self):
        """Test creation of a Q instance with multiple keyword arguments - with one Decimal value"""
        q = Q(table_field__iexact=decimal.Decimal('17.357'),
              table_section_gte=23)

        # A Q object with multiple keyword arguments are anded together
        self.assertEqual([(k, v) for k, v in q._members],
                         [('table_field__iexact', decimal.Decimal('17.357')),
                          ('table_section_gte', 23)])
        self.assertEqual(q._operator, 'AND')
        self.assertFalse(q._negated)

    def test_510_106_two_argumentQ_date(self):
        """Test creation of a Q instance with multiple keyword arguments - with one date value"""
        q = Q(table_field__iexact=datetime.date(year=2011, month=8, day=13),
              table_section_gte=23)

        # A Q object with multiple keyword arguments are anded together
        self.assertEqual([(k, v) for k, v in q._members],
                         [('table_field__iexact',
                           datetime.date(year=2011, month=8, day=13)),
                          ('table_section_gte', 23)])
        self.assertEqual(q._operator, 'AND')
        self.assertFalse(q._negated)

    def test_510_107_two_argumentQ_datetime(self):
        """Test creation of a Q instance with multiple keyword arguments - with one datetime value"""
        q = Q(table_field__iexact=datetime.datetime(year=2011, month=8, day=13,
                                                    hour=13, minute=35,
                                                    second=45,
                                                    microsecond=450),
              table_section_gte=23)

        # A Q object with multiple keyword arguments are anded together
        self.assertEqual([(k, v) for k, v in q._members],
                         [('table_field__iexact',
                           datetime.datetime(year=2011, month=8, day=13,
                                             hour=13, minute=35,
                                             second=45, microsecond=450)),
                          ('table_section_gte', 23)])
        self.assertEqual(q._operator, 'AND')
        self.assertFalse(q._negated)

    def test_510_108_two_argumentQ_timedelta(self):
        """Test creation of a Q instance with multiple keyword arguments - with one timedelta value"""
        q = Q(table_field__iexact=datetime.timedelta(days=173, seconds=543,
                                                     microseconds=947),
              table_section_gte=23)

        # A Q object with multiple keyword arguments are anded together
        self.assertEqual([(k, v) for k, v in q._members],
                         [('table_field__iexact',
                           datetime.timedelta(days=173, seconds=543,
                                              microseconds=947)),
                          ('table_section_gte', 23)])
        self.assertEqual(q._operator, 'AND')
        self.assertFalse(q._negated)

    def test_510_200_two_anded_together(self):
        """Test that two objects can be anded together"""

        q1 = Q(table_field_lte=17)
        q2 = Q(table_section_gte=18)

        with Invariant(q1, q2):
            q3 = q1 & q2

        self.assertEqual(q3._members, [q1, q2])
        self.assertEqual(q3._operator, 'AND')

    def test_510_201_two_ored_together(self):
        """Test that two objects can be ored together"""
        q1 = Q(table_field_lte=17)
        q2 = Q(table_section_gte=18)
        with Invariant(q1, q2):
            q3 = q1 | q2

        self.assertEqual(q3._members, [q1, q2])
        self.assertEqual(q3._operator, 'OR')

    def test_510_202_two_anded_together_one_negated(self):
        """Test that two objects can be anded together when one is negated"""
        q1 = Q(table_field_lte=17)
        q2 = Q(table_section_gte=18)

        with Invariant(q1, q2):
            q3 = q1 | ~q2

        self.assertFalse(q2._negated)

        self.assertEqual(q3._members, [q1, ~q2])
        self.assertEqual(q3._operator, 'OR')

    def test_510_203_two_anded_together_both_negated(self):
        """Test that two objects can be anded together with both negated"""
        q1 = Q(table_field_lte=17)
        q2 = Q(table_section_gte=18)

        with Invariant(q1, q2):
            q3 = ~q1 | ~q2

        self.assertEqual(q3._members, [~q1, ~q2])
        self.assertEqual(q3._operator, 'OR')


class TestQSQL(unittest.TestCase):
    """
    Test that Q objects can generate SQL fragments

    """
    def setUp(self):
        """Setup Engine Mock and resolve_lookup method"""

        def resolve_lookup( lookup, value, model=None, joins=None):
            """Dummy resolve__lookup method"""
            lookup_format = {'name__exact': 'name = {!r}',
                             'name__gte':'name >= {!r}',
                             'address__exact':'address={!r}',
                             'address__contains': 'address like \'%{}%\''}
            f = lookup_format[lookup]
            return f.format(value)

        self.test_engine = MagicMock(autospec=EngineCore)
        self.test_engine.resolve_lookup=Mock(side_effect=resolve_lookup)
        self.joins = MagicMock(autospec=list)
        self.test_model = MagicMock(autospec=Model)

    def test_510_300_SQL_creation_simple_Q(self):
        """Test that the lookups in a Q object are executed as expected."""

        q1 = Q(name__gte=23)
        sql = q1.resolve(engine=self.test_engine, model=self.test_model, joins=self.joins)

        # Confirm that the resolve lookup has been called as expected
        self.test_engine.resolve_lookup.assert_has_calls(calls=[call('name__gte', 23, model=self.test_model, joins=self.joins)])

        # Confirm that the expected sql is created
        self.assertEqual(sql,'(name >= 23)')

    def test_510_301_SQL_creation_simple_negated_Q(self):
        """Test that the lookups in a negated Q object are executed as expected."""

        q1 = ~Q(name__exact='hello')

        sql = q1.resolve(engine=self.test_engine, model=self.test_model, joins=self.joins)

        # Confirm that the resolve lookup has been called as expected
        self.test_engine.resolve_lookup.assert_has_calls(calls=[call('name__exact', 'hello', model=self.test_model, joins=self.joins)])

        # Confirm that the expected sql is created
        self.assertEqual(sql,'NOT (name = \'hello\')')

    def test_510_302_SQL_creation_complex_Q(self):
        """Test that the lookups in a complex Q object are executed as expected."""

        q1 = Q(name__exact='hello') | Q(address__contains='Brantham')

        sql = q1.resolve(engine=self.test_engine, model=self.test_model, joins=self.joins)

        # Confirm that the resolve lookup has been called as expected
        self.test_engine.resolve_lookup.assert_has_calls(calls=[
            call('name__exact', 'hello', model=self.test_model, joins=self.joins),
            call('address__contains', 'Brantham', model=self.test_model, joins=self.joins)])

        # Confirm that the expected sql is created
        self.assertEqual(sql, '((name = \'hello\') OR (address like \'%Brantham%\'))')

    def test_510_303_SQL_creation_complex_Q(self):
        """Test that the lookups in a complex Q with and and or"""

        q1 = Q(name__exact='hello', name__gte='Hello') | Q(name__gte='Ipswich')

        sql = q1.resolve(engine=self.test_engine, model=self.test_model, joins=self.joins)

        # Confirm that the resolve lookup has been called as expected
        self.test_engine.resolve_lookup.assert_has_calls(calls=[
            call('name__exact', 'hello', model=self.test_model, joins=self.joins),
            call('name__gte', 'Hello', model=self.test_model, joins=self.joins),
            call('name__gte', 'Ipswich', model=self.test_model, joins=self.joins)],
            any_order = True)

        # Confirm that the expected sql is created
        self.assertEqual(sql, '((name = \'hello\' AND name >= \'Hello\') OR (name >= \'Ipswich\'))')


class TestF(unittest.TestCase):
    # noinspection PyMissingOrEmptyDocstring
    def setUp(self):
        pass

    # noinspection PyMissingOrEmptyDocstring
    def tearDown(self):
        pass

    def test_520_000_basic_F_object(self):
        """Test basic F object creation - single field"""
        f = F('test__name')
        self.assertEqual(F('test__name'), f)

    def test_520_001_basic_negation(self):
        """Test basic F object creation - single field with negation"""
        f = F('test__name')
        with Invariant(f):
            f1 = -f

        self.assertIsNotNone(f1)
        self.assertEqual(-F('test__name'), f1)
        self.assertTrue(f1._negate)

    def test_520_010_basic_Addition(self):
        """Test Addition of F object and numeric"""
        f = F('test__name')
        with Invariant(f):
            f1 = f + 10
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') + 10, f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, 10)
        self.assertEqual(f1._operator, '+')

    def test_520_011_basic_Subtraction(self):
        """Test Subtraction of F object and numeric"""
        f = F('test__name')
        with Invariant(f):
            f1 = f - 10
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') - 10, f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, 10)
        self.assertEqual(f1._operator, '-')

    def test_520_012_basic_Multi(self):
        """Test Multiplication of F object and numeric"""
        f = F('test__name')
        with Invariant(f):
            f1 = f * 10
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') * 10, f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, 10)
        self.assertEqual(f1._operator, '*')

    def test_520_013_basic_Division(self):
        """Test Division of F object by numeric"""
        f = F('test__name')
        with Invariant(f):
            f1 = f / 10
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') / 10, f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, 10)
        self.assertEqual(f1._operator, '/')

    def test_520_014_basic_lshift(self):
        """Test lshift of F object by numeric"""
        f = F('test__name')
        with Invariant(f):
            f1 = f << 10
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') << 10, f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, 10)
        self.assertEqual(f1._operator, '<<')

    def test_520_015_basic_rshift(self):
        """Test rshift of F object by numeric"""
        f = F('test__name')
        with Invariant(f):
            f1 = f >> 10
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') >> 10, f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, 10)
        self.assertEqual(f1._operator, '>>')

    def test_520_016_basic_xor(self):
        """Test xor of F object with numeric"""
        f = F('test__name')
        with Invariant(f):
            f1 = f ^ 10
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') ^ 10, f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, 10)
        self.assertEqual(f1._operator, '^')

    def test_520_017_basic_and(self):
        """Test and of F object with numeric"""
        f = F('test__name')
        with Invariant(f):
            f1 = f & 10
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') & 10, f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, 10)
        self.assertEqual(f1._operator, '&')

    def test_520_018_basic_or(self):
        """Test or of F object with numeric"""
        f = F('test__name')
        with Invariant(f):
            f1 = f | 10
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') | 10, f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, 10)
        self.assertEqual(f1._operator, '|')

    def test_520_019_basic_mod(self):
        """Test mod of F object with numeric"""
        f = F('test__name')
        with Invariant(f):
            f1 = f % 10
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') % 10, f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, 10)
        self.assertEqual(f1._operator, '%')

    def test_520_050_basic_Addition(self):
        """Test addition of two F objects"""
        f = F('test__name')
        with Invariant(f):
            f1 = f + F('test__group')
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') + F('test__group'), f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, F('test__group'))
        self.assertEqual(f1._operator, '+')

    def test_520_051_basic_Subtraction(self):
        """Test subtraction of two F objects"""
        f = F('test__name')
        with Invariant(f):
            f1 = f - F('test__group')
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') - F('test__group'), f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, F('test__group'))
        self.assertEqual(f1._operator, '-')

    def test_520_052_basic_Multi(self):
        """Test multiplication of two F objects"""
        f = F('test__name')
        with Invariant(f):
            f1 = f * F('test__group')
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') * F('test__group'), f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, F('test__group'))
        self.assertEqual(f1._operator, '*')

    def test_520_053_basic_Division(self):
        """Test division of one F object with another"""
        f = F('test__name')
        with Invariant(f):
            f1 = f / F('test__group')
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') / F('test__group'), f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, F('test__group'))
        self.assertEqual(f1._operator, '/')

    def test_520_054_basic_lshift(self):
        """Test lshift of one F object by another"""
        f = F('test__name')
        with Invariant(f):
            f1 = f << F('test__group')
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') << F('test__group'), f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, F('test__group'))
        self.assertEqual(f1._operator, '<<')

    def test_520_055_basic_rshift(self):
        """Test rshift of one F object by another"""
        f = F('test__name')
        with Invariant(f):
            f1 = f >> F('test__group')
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') >> F('test__group'), f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, F('test__group'))
        self.assertEqual(f1._operator, '>>')

    def test_520_056_basic_xor(self):
        """Test xor of one F object by another"""
        f = F('test__name')
        with Invariant(f):
            f1 = f ^ F('test__group')
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') ^ F('test__group'), f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, F('test__group'))
        self.assertEqual(f1._operator, '^')

    def test_520_057_basic_and(self):
        """Test and of one F object by another"""
        f = F('test__name')
        with Invariant(f):
            f1 = f & F('test__group')
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') & F('test__group'), f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, F('test__group'))
        self.assertEqual(f1._operator, '&')

    def test_520_058_basic_or(self):
        """Test or of one F object by another"""
        f = F('test__name')
        with Invariant(f):
            f1 = f | F('test__group')
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') | F('test__group'), f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, F('test__group'))
        self.assertEqual(f1._operator, '|')

    def test_520_059_basic_mod(self):
        """Test mod of one F object by another"""
        f = F('test__name')
        with Invariant(f):
            f1 = f % F('test__group')
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') % F('test__group'), f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, F('test__group'))
        self.assertEqual(f1._operator, '%')

    def test_520_060_basic_concat(self):
        """Test concatenation of a string with an F object"""
        f = F('test__name')
        with Invariant(f):
            f1 = 'hello' + f
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual('hello' + F('test__name'), f1)
        self.assertEqual(f1._lhs, 'hello')
        self.assertEqual(f1._rhs, F('test__name'))
        self.assertEqual(f1._operator, '+')

    def test_520_061_basic_concat(self):
        """Test concatenation of a F object with a string"""
        f = F('test__name')
        with Invariant(f):
            f1 = f + 'hello'
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') + 'hello', f1)
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._rhs, 'hello')
        self.assertEqual(f1._operator, '+')

    def test_520_062_addition_of_non_integer(self):
        """Test addition of a F object with a non numeric"""
        f = F('test__name')
        with Invariant(f):
            f1 = f + datetime.date(2012, 3, 19)
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(F('test__name') + datetime.date(2012, 3, 19), f1)
        self.assertEqual(f1._rhs, datetime.date(2012, 3, 19))
        self.assertEqual(f1._lhs, F('test__name'))
        self.assertEqual(f1._operator, '+')

    def test_520_070_Combing_terms_addition_with_brackets(self):
        """Test multi-level combination of F objects a*(b+c)"""
        f = (F('x') + F('y')) * F('z')
        self.assertIsNotNone(f)
        self.assertIsInstance(f, F)
        self.assertEqual((F('x') + F('y')) * F('z'), f)
        self.assertEqual(f._lhs, (F('x') + F('y')))
        self.assertEqual(f._rhs, F('z'))
        self.assertEqual(f._operator, '*')

    def test_520_071_Combing_terms_multiplication_with_addition(self):
        """Test multi-level combination of F objects a*b+c)"""
        f = F('x') * F('y') + F('z')
        self.assertIsNotNone(f)
        self.assertIsInstance(f, F)
        self.assertEqual((F('x') * F('y')) + F('z'), f)
        self.assertEqual(f._lhs, (F('x') * F('y')))
        self.assertEqual(f._rhs, F('z'))
        self.assertEqual(f._operator, '+')

    def test_520_072_negation_of_combined_exp(self):
        """Test negation of a combined expression"""
        f = F('x') + F('y')
        self.assertIsNotNone(f)
        with Invariant(f):
            f1 = -f
        self.assertIsNotNone(f1)
        self.assertIsInstance(f1, F)
        self.assertEqual(f1, -(F('x') + F('y')))


class TestFSQL(unittest.TestCase):

    def setUp(self):

        def resolve(field, engine=None, model=None, joins=None):
            """Naive field name resolution method - we only case that the SQL uses the column name that this method returns"""
            c_name =  field + '_column'
            joins.append(field + '_join')
            return c_name

        self.engine = MagicMock(autospec=EngineCore)
        self.model = MagicMock(autospec=Model)
        self.engine.resolve_name = Mock(side_effect=resolve)
        self.joins = []

    def test_520_100_sql_creation_simple_F_object(self):
        """A Simple F object is resolved to the field name

           The Engine resolve method is mocked out - what we care is that the engine is called.
        """
        f = F('name')
        sql = f.resolve(engine=self.engine, model=self.model, joins=self.joins)

        self.engine.resolve_name.assert_called_once_with('name', model=self.model, joins=self.joins)
        self.assertEqual(sql, 'name_column')
        self.assertEqual(self.joins, ['name_join'])

    def test_520_101_sql_creation_additive_F_object(self):
        """Test SQL generation for a additive F object"""
        f = F('name') + F('age')

        sql = f.resolve(engine=self.engine, model=self.model, joins=self.joins)

        self.engine.resolve_name.assert_has_calls(calls=[call('name',model=self.model, joins=self.joins),
                                                         call('age',model=self.model, joins=self.joins),])
        self.assertEqual(sql, '(name_column+age_column)')
        self.assertEqual(Counter(self.joins), Counter(['name_join','age_join']))

    def test_520_102_sql_creation_F_object_with_constant(self):
        """Test SQL generation of F object with a constant"""

        f = F('name') * 23
        sql = f.resolve(engine=self.engine, model=self.model, joins=self.joins)

        # Confirm correct SQL is created
        self.assertEqual(sql, '(name_column*23)')

        # Confirm that the right engine method is called as expected
        self.engine.resolve_name.assert_has_calls(calls=[call('name',model=self.model, joins=self.joins),])
        self.assertEqual(Counter(self.joins), Counter(['name_join']))

    def test_520_103_sql_creation_complex_F_object(self):
        """Test F object sql creation with multi-layer F object"""

        f = (F('name') + F('age')) * F('salary')
        sql = f.resolve(engine=self.engine, model=self.model, joins=self.joins)

        # Confirm correct SQL is created
        self.assertEqual(sql, '((name_column+age_column)*salary_column)')

        # Confirm that the right engine method is called as expected
        self.engine.resolve_name.assert_has_calls(
                calls=[call('name',model=self.model, joins=self.joins),
                        call('age',model=self.model, joins=self.joins),
                        call('salary',model=self.model, joins=self.joins),])

        # Confirm that the join data from the resolve method is being returned.
        self.assertEqual(Counter(self.joins),
                         Counter(['name_join', 'age_join', 'salary_join']))

    def test_520_104_sql_creation_complex_F_object_prcedence(self):
        """Test SQL creation with multi-layer F object """

        f = F('salary') + F('salary') * F('bonus_rate')
        sql = f.resolve(engine=self.engine, model=self.model, joins=self.joins)

        # Confim the right SQL is generated - and the right joins are recorded
        self.assertEqual(sql, '(salary_column+(salary_column*bonus_rate_column))')

        # Confirm that the right engine method is called as expected
        self.engine.resolve_name.assert_has_calls(
                calls=[call('salary',model=self.model, joins=self.joins),
                        call('bonus_rate',model=self.model, joins=self.joins),
                        call('salary',model=self.model, joins=self.joins),],
                any_order=True)

        self.assertEqual(Counter(self.joins), Counter(['salary_join', 'salary_join','bonus_rate_join']))


    # Test the various classes within the Query Heirarchy
    #
    #    tests 530
    #        000 to 099 - BaseQuery
    #        100 to 199 - OrderingAndLimits
    #        200 to 299 - FilterableQuery
    #        300 to 399 - RawSQL
    #        400 to 450 - Combination (and Union, Intersect & Difference)
    #        500 to 599   Table Info and Join
    #        600 to 699 - SimpleQuery

class TestBaseQuery(unittest.TestCase):

    # noinspection PyMissingOrEmptyDocstring
    def setUp(self):
        pass

    #
    # The Base Query Class
    # The Base Query is simply a set of informational flags
    # Provides a common interface for all of the different types of Query classes.
    # Allows code higher up to test flags rather than test classes and subclasses
    #
    def test_530_000_BaseQuery_Creation(self):
        """Can we create a BaseQuery object as expected"""
        bq = BaseQuery()
        self.assertTrue(bq.is_mutable)
        self.assertTrue(bq.is_extendable)
        self.assertTrue(bq.is_filterable)
        self.assertTrue(bq.is_orderable)
        self.assertTrue(bq.is_limitable)

    def test_530_001_BaseQuery_Creation_Immuatble(self):
        """Can we create a BaseQuery object recorded as immutable"""
        bq = BaseQuery(mutable=False)
        self.assertFalse(bq.is_mutable)
        self.assertFalse(bq.is_extendable)
        self.assertFalse(bq.is_filterable)
        self.assertFalse(bq.is_orderable)
        self.assertFalse(bq.is_limitable)

    def test_530_010_BaseQuery_Creation_Immuatble_overides_extendable(self):
        """Can we create a BaseQuery object recorded as immutable cannot be extendable"""
        bq = BaseQuery(mutable=False, extendable=True)
        self.assertFalse(bq.is_mutable)
        self.assertFalse(bq.is_extendable)
        self.assertFalse(bq.is_filterable)
        self.assertFalse(bq.is_orderable)
        self.assertFalse(bq.is_limitable)

    def test_530_021_BaseQuery_Creation_Immuatble_overides_filterable(self):
        """Can we create a BaseQuery object recorded as immutable cannot be filterable"""
        bq = BaseQuery(mutable=False, filterable=True)
        self.assertFalse(bq.is_mutable)
        self.assertFalse(bq.is_extendable)
        self.assertFalse(bq.is_filterable)
        self.assertFalse(bq.is_orderable)
        self.assertFalse(bq.is_limitable)

    def test_530_022_BaseQuery_Creation_Immuatble_overides_orderable(self):
        """Can we create a BaseQuery object recorded as immutable cannot be orderable"""
        bq = BaseQuery(mutable=False, orderable=True)
        self.assertFalse(bq.is_mutable)
        self.assertFalse(bq.is_extendable)
        self.assertFalse(bq.is_filterable)
        self.assertFalse(bq.is_orderable)
        self.assertFalse(bq.is_limitable)

    def test_530_023_BaseQuery_Creation_Immuatble_overides_limitable(self):
        """Can we create a BaseQuery object recorded as immutable cannot be limitable"""
        bq = BaseQuery(mutable=False, limitable=True)
        self.assertFalse(bq.is_mutable)
        self.assertFalse(bq.is_extendable)
        self.assertFalse(bq.is_filterable)
        self.assertFalse(bq.is_orderable)
        self.assertFalse(bq.is_limitable)

    def test_530_030_BaseQuery_Creation_Mutable_and_not_extendable(self):
        """Can we create a BaseQuery object which is mutable but not extendable"""
        bq = BaseQuery(extendable=False)
        self.assertTrue(bq.is_mutable)
        self.assertFalse(bq.is_extendable)
        self.assertTrue(bq.is_filterable)
        self.assertTrue(bq.is_orderable)
        self.assertTrue(bq.is_limitable)

    def test_530_031_BaseQuery_Creation_Mutable_and_not_filterable(self):
        """Can we create a BaseQuery object which is mutable but not filterable"""
        bq = BaseQuery(filterable=False)
        self.assertTrue(bq.is_mutable)
        self.assertTrue(bq.is_extendable)
        self.assertFalse(bq.is_filterable)
        self.assertTrue(bq.is_orderable)
        self.assertTrue(bq.is_limitable)

    def test_530_030_BaseQuery_Creation_Mutable_and_not_orderable(self):
        """Can we create a BaseQuery object which is mutable but not orderable"""
        bq = BaseQuery(orderable=False)
        self.assertTrue(bq.is_mutable)
        self.assertTrue(bq.is_extendable)
        self.assertTrue(bq.is_filterable)
        self.assertFalse(bq.is_orderable)
        self.assertTrue(bq.is_limitable)

    def test_530_030_BaseQuery_Creation_Mutable_and_not_limitable(self):
        """Can we create a BaseQuery object which is mutable but not limitable"""
        bq = BaseQuery(limitable=False)
        self.assertTrue(bq.is_mutable)
        self.assertTrue(bq.is_extendable)
        self.assertTrue(bq.is_filterable)
        self.assertTrue(bq.is_orderable)
        self.assertFalse(bq.is_limitable)

class TestOrderingAndLimits(unittest.TestCase):
    #
    # Testing Ordering & Limits class
    # This class forms a base class for the SImple Query and Combination classes.
    #

    def setUp(self):
        pass

    def test_530_100_OrderingAndLimits_Creation(self):
        """Test creation of eempty OrderingAndLimits instance"""
        a = OrderingAndLimits()
        self.assertEqual(a.order_by, [])
        self.assertEqual(a.limits, [])
        self.assertTrue(a.is_limitable)
        self.assertTrue(a.is_orderable)

    def test_530_100a_OrderingAndLimits_Creation_Passthrough(self):
        """Test creation of empty OrderingAndLimits instance, which pases through the extendable and filterable settings"""
        a = OrderingAndLimits(extendable=False, filterable=False)
        self.assertFalse(a.is_extendable)
        self.assertFalse(a.is_filterable)
        self.assertTrue(a.is_limitable)
        self.assertTrue(a.is_orderable)

    def test_530_101_OrderingAndLimits_adding_ordering(self):
        """Test setting of a single orderby element which is an simple string """
        a = OrderingAndLimits()
        a.add_order_by('test__name')
        self.assertEqual(a.order_by, ['test__name'])
        self.assertEqual(a.limits, [])

    def test_530_102_OrderingAndLimits_adding_ordering_F_object(self):
        """Test setting of a single orderby element which is a numeric """
        a = OrderingAndLimits()
        a.add_order_by(1)
        self.assertEqual(a.order_by, [1])
        self.assertEqual(a.limits, [])

    def test_530_103_OrderingAndLimits_adding_ordering_F_object(self):
        """Test setting of two orderby element of different types"""
        a = OrderingAndLimits()
        a.add_order_by(1, 'test__x')
        self.assertEqual(a.order_by, [1, 'test__x'])
        self.assertEqual(a.limits, [])

    def test_530_104_OrderingAndLimits_inverting_with_Complex_object(self):
        """Test inverting of two orderby element"""
        a = OrderingAndLimits()
        a.add_order_by(1, 'test__x')
        a.invert_ordering()
        self.assertEqual(a.order_by, [-1, '-test__x'])
        self.assertEqual(a.limits, [])

    def test_530_104_OrderingAndLimits_Limits(self):
        """Test adding of a single limit element"""
        a = OrderingAndLimits()
        a.set_limits(1)
        self.assertEqual(a.limits, [1])

    def test_530_105_OrderingAndLimits_Limits_TwoArgs(self):
        """Test adding of a two limit element"""
        a = OrderingAndLimits()
        a.set_limits(1, 25)
        self.assertEqual(a.limits, [1, 25])

    def test_530_106_OrderingAndLimits_Limits_ThreeArgs(self):
        """Test that you can't add three limit values"""
        a = OrderingAndLimits()
        with self.assertRaises(exceptions.LimitsError):
            a.set_limits(1, 25, 18)

    def test_530_107_OrderingAndLimits_Limits_one_then_two(self):
        """Test that you can't add two when is 1 is already recorded"""
        a = OrderingAndLimits(limits=[1])
        self.assertEqual(a.limits, [1])
        a.set_limits(25, 18)
        self.assertEqual(a.limits, [25, 18])

    def test_530_108_clear_limits(self):
        """Test that you can clear any limits that have been set"""
        a = OrderingAndLimits()
        a.set_limits(1, 25)
        self.assertEqual(a.limits, [1, 25])
        a.clear_limits()
        self.assertEqual(a.limits, [])

class TestFilterableQuery(unittest.TestCase):
    #
    # Test a filterable query
    #

    def setUp(self):
        pass

    def test_530_200_FilterableQuery(self):
        """Can we build a filterable Query instance"""
        fq = FilterableQuery()
        self.assertIsInstance(fq, OrderingAndLimits)
        self.assertEqual(fq.criteria, Q())
        self.assertTrue(fq.is_filterable)
        self.assertTrue(fq.is_orderable)
        self.assertTrue(fq.is_limitable)

    def test_530_201_FilterableQuery_query_pass_through(self):
        """Test FilterableQuery with a preset criteria"""
        fq = FilterableQuery(criteria=Q(test=73))
        self.assertIsInstance(fq, OrderingAndLimits)
        self.assertEqual(fq.criteria, Q(test=73))
        self.assertTrue(fq.is_filterable)
        self.assertTrue(fq.is_orderable)
        self.assertTrue(fq.is_limitable)

    def test_530_202_FilterableQuery_order_by_pass_through(self):
        """Test FilterableQuery with a preset criteria and an order by """
        fq = FilterableQuery(criteria=Q(test=73), order_by=[1, 2])
        self.assertIsInstance(fq, OrderingAndLimits)
        self.assertEqual(fq.criteria, Q(test=73))
        self.assertEqual(fq.order_by, [1, 2])
        self.assertTrue(fq.is_filterable)
        self.assertTrue(fq.is_orderable)
        self.assertTrue(fq.is_limitable)

    def test_530_203_FilterableQuery_limitable_pass_through(self):
        """Test FilterableQuery with a but turn off limitable"""
        fq = FilterableQuery(limitable=False)
        self.assertIsInstance(fq, OrderingAndLimits)
        self.assertEqual(fq.criteria, Q())
        self.assertTrue(fq.is_filterable)
        self.assertTrue(fq.is_orderable)
        self.assertFalse(fq.is_limitable)

    def test_530_210_FilterableQuery_set_criteria(self):
        """Test FilterableQuery criteria property"""
        fq = FilterableQuery()
        fq.criteria = Q(test_name=17)
        self.assertEqual(fq.criteria, Q(test_name=17))

    def test_530_211_FilterableQuery_set_complex_or(self):
        """Test FilterableQuery criteria with an or condition"""
        fq = FilterableQuery()
        fq.criteria |= Q(test_name=17) | Q(test_name=16)
        self.assertIsInstance(fq, OrderingAndLimits)
        self.assertEqual(fq.criteria, Q(test_name=17) | Q(test_name=16))

    def test_530_212_FilterableQuery_set_complex_and(self):
        """Test FilterableQuery criteria with an and condition"""
        fq = FilterableQuery()
        fq.criteria = Q(test_name=17) | Q(test_name=16)
        fq.criteria &= Q(test_name=18)
        self.assertIsInstance(fq, OrderingAndLimits)
        self.assertEqual(fq.criteria,
                         (Q(test_name=17) | Q(test_name=16)) & Q(test_name=18))



class TestRawSQL(unittest.TestCase):
    #
    # Test RawSQL
    #
    def setUp(self):
         pass

    def test_530_300_RawSQL_creation(self):
        """Test construction of RAWSQL query class"""
        query = 'SELECT * from test where test.x=test.y'
        qs = RawSQL(sql=query, parameters=None)
        self.assertEqual(qs._sql, query)
        self.assertIsNone(qs._paramters)
        self.assertFalse(qs.is_mutable)

    def test_530_301_RawSQL_creation_with_params(self):
        """Test construction of RAWSQL query class and parameters"""
        query = 'SELECT * from test where test.x=test.y'
        params = [(1, 2, 3), (4, 5, 6), (7, 8, 0)]
        qs = RawSQL(sql=query, parameters=params)
        self.assertEqual(qs._sql, query)
        self.assertEqual(qs._paramters, params)
        self.assertFalse(qs.is_mutable)

class TestCombination(unittest.TestCase):
    #
    # Test Combination, Union, Intersection & Union classes
    #
    def setUp(self):
        pass

    def test_530_400_combination_creation(self):
        """Test the creation of a Combination super class"""
        c = Combination()
        self.assertNotIsInstance(c, FilterableQuery)
        self.assertIsInstance(c, OrderingAndLimits)
        self.assertTrue(c.is_orderable)
        self.assertTrue(c.is_limitable)
        self.assertFalse(c.is_extendable)
        self.assertFalse(c.is_filterable)
        self.assertEqual(c.order_by, [])
        self.assertEqual(c.limits, [])
        self.assertEqual(c.queries, [])

    def test_530_401_combination_creation(self):
        """Test the creation of a combination with starting querys"""
        qs = (MagicMock(spenc=BaseQuery, name='BQ1'),
              MagicMock(spenc=BaseQuery, name='BQ2'),
              MagicMock(spenc=BaseQuery, name='BQ3'))
        qs[0].__repr__ = Mock(return_value='BQ1')
        qs[1].__repr__ = Mock(return_value='BQ2')
        qs[2].__repr__ = Mock(return_value='BQ3')
        c = Combination(*qs)
        self.assertEqual(c.queries, [*qs])

    def test_530_402_combination_creation_with_order(self):
        """Test the creation of a combination with starting querys and an order"""
        qs = (MagicMock(spenc=BaseQuery, name='BQ1'),
              MagicMock(spenc=BaseQuery, name='BQ2'),
              MagicMock(spenc=BaseQuery, name='BQ3'))
        qs[0].__repr__ = Mock(return_value='BQ1')
        qs[1].__repr__ = Mock(return_value='BQ2')
        qs[2].__repr__ = Mock(return_value='BQ3')
        order = (1, 2, 3, 4)
        c = Combination(*qs, order_by=order)
        self.assertEqual(c.queries, [*qs])
        self.assertEqual(c.order_by, order)

    #
    # Test Union
    #
    def test_530_420_Union_creation(self):
        """Test creation of the Union Class"""
        u = Union()
        self.assertIsInstance(u, Combination)
        self.assertNotIsInstance(u, FilterableQuery)
        self.assertIsInstance(u, OrderingAndLimits)
        self.assertFalse(u.is_filterable)
        self.assertFalse(u.is_extendable)
        self.assertTrue(u.is_orderable)
        self.assertTrue(u.is_limitable)
        self.assertEqual(u.queries, [])
        self.assertFalse(u.get_all)

    def test_530_421_Union_creation(self):
        """Test creation of the Union Class with queries"""
        qs = (MagicMock(spenc=BaseQuery, name='BQ1'),
              MagicMock(spenc=BaseQuery, name='BQ2'),
              MagicMock(spenc=BaseQuery, name='BQ3'))
        qs[0].__repr__ = Mock(return_value='BQ1')
        qs[1].__repr__ = Mock(return_value='BQ2')
        qs[2].__repr__ = Mock(return_value='BQ3')
        u = Union(*qs)
        self.assertEqual(u.queries, list(qs))
        self.assertFalse(u.get_all)

    def test_530_421_Union_creation_get_all(self):
        """Test creation of the Union Class with queries"""
        qs = (MagicMock(spenc=BaseQuery, name='BQ1'),
              MagicMock(spenc=BaseQuery, name='BQ2'),
              MagicMock(spenc=BaseQuery, name='BQ3'))
        qs[0].__repr__ = Mock(return_value='BQ1')
        qs[1].__repr__ = Mock(return_value='BQ2')
        qs[2].__repr__ = Mock(return_value='BQ3')
        u = Union(*qs, get_all=True)
        self.assertEqual(u.queries, list(qs))
        self.assertTrue(u.get_all)

    #
    # Test Intersection
    #
    def test_530_430_Intersection_creation(self):
        """Test creation of the Intersection Class"""
        u = Intersection()
        self.assertIsInstance(u, Combination)
        self.assertNotIsInstance(u, FilterableQuery)
        self.assertIsInstance(u, OrderingAndLimits)
        self.assertFalse(u.is_filterable)
        self.assertFalse(u.is_extendable)
        self.assertTrue(u.is_orderable)
        self.assertTrue(u.is_limitable)
        self.assertEqual(u.queries, [])

    def test_530_421_Intersection_creation(self):
        """Test creation of the Union Class with queries"""
        qs = (MagicMock(spenc=BaseQuery, name='BQ1'),
              MagicMock(spenc=BaseQuery, name='BQ2'),
              MagicMock(spenc=BaseQuery, name='BQ3'))
        qs[0].__repr__ = Mock(return_value='BQ1')
        qs[1].__repr__ = Mock(return_value='BQ2')
        qs[2].__repr__ = Mock(return_value='BQ3')
        u = Intersection(*qs)
        self.assertEqual(u.queries, list(qs))

    #
    # Test Difference
    #
    def test_530_430_Difference_creation(self):
        """Test creation of the Intersection Class"""
        u = Difference()
        self.assertIsInstance(u, Combination)
        self.assertNotIsInstance(u, FilterableQuery)
        self.assertIsInstance(u, OrderingAndLimits)
        self.assertFalse(u.is_filterable)
        self.assertFalse(u.is_extendable)
        self.assertTrue(u.is_orderable)
        self.assertTrue(u.is_limitable)
        self.assertEqual(u.queries, [])

    def test_530_431_Difference_creation(self):
        """Test creation of the Union Class with queries"""
        qs = (MagicMock(spenc=BaseQuery, name='BQ1'),
              MagicMock(spenc=BaseQuery, name='BQ2'),
              MagicMock(spenc=BaseQuery, name='BQ3'))
        qs[0].__repr__ = Mock(return_value='BQ1')
        qs[1].__repr__ = Mock(return_value='BQ2')
        qs[2].__repr__ = Mock(return_value='BQ3')
        u = Difference(*qs)
        self.assertEqual(u.queries, list(qs))

class TestJoin(unittest.TestCase):
    """Test the Join class and the nodes that repesent the joins being created"""

    def setUp(self):
        """Set up mock objects for testing join creation"""
        self.modelA = MagicMock(autospec=Model, name='ModelA')
        self.modelA.table_name = Mock(return_value='ModelA')

        self.modelB = MagicMock(autospec=Model, name='ModelB')
        self.modelB.table_name = Mock(return_value='ModelB')

        self.modelC = MagicMock(autospec=Model, name='ModelC')
        self.modelC.table_name = Mock(return_value='ModelC')

        def get_relationship(model_name, relationship_name):
            rels = {'modelA':{'owner':(self.modelB, 'id', 'id'),
                              'location':(self.modelB,'id','location')},
                    'modelB':{'orders':(self.modelC,'orderid','id')}
                    }
            return rels[model_name].get(relationship_name,None)

        self.modelA.get_relationship= Mock(side_effect=partial(get_relationship,'modelA'))
        self.modelB.get_relationship= Mock(side_effect=partial(get_relationship,'modelB'))

    def test_530_500_Join_creation(self):
        """Test that a simple Join instance can be created"""
        j = Join(root_model=self.modelA)
        joins = [ (name, node) for name, node in j.items()]

        self.assertEqual(len(joins),1)
        name, node = joins[0]

        self.assertEqual(name, '')
        self.assertEqual(node.model, self.modelA)
        self.assertEqual(node.relation, '')
        self.assertEqual(node.fields,())

    def test_530_501_Add_join_single_child(self):
        """Test creation of a join with a relation"""
        j = Join(root_model=self.modelA)
        j.addJoin('owner')
        joins = [ (name, node) for name, node in j.items()]

        self.assertEqual(len(joins),2)
        name, node = joins[0]

        self.assertEqual(name, 'ModelA')
        self.assertEqual(node.model, self.modelA)
        self.assertEqual(node.relation, 'ModelA')
        self.assertEqual(node.fields,())

        name, node = joins[1]
        self.assertEqual(name, 'ModelA__owner')
        self.assertEqual(node.model, self.modelB)
        self.assertEqual(node.relation, 'ModelA__owner')
        self.assertEqual(node.fields,('id','id'))

    def test_530_502_Add_joins_2_children(self):
        """Test creation of two relations - both children of the main table"""
        j = Join(root_model=self.modelA)
        j.addJoin('owner')
        j.addJoin('location')

        joins = [ (name, node) for name, node in j.items()]

        self.assertEqual(len(joins),3)
        name, node = joins[0]

        self.assertEqual(name, 'ModelA')
        self.assertEqual(node.model, self.modelA)
        self.assertEqual(node.relation, 'ModelA')
        self.assertEqual(node.fields,())

        name, node = joins[1]
        self.assertEqual(name, 'ModelA__owner')
        self.assertEqual(node.model, self.modelB)
        self.assertEqual(node.relation, 'ModelA__owner')
        self.assertEqual(node.fields,('id','id'))

        name, node = joins[2]
        self.assertEqual(name, 'ModelA__location')
        self.assertEqual(node.model, self.modelB)
        self.assertEqual(node.relation, 'ModelA__location')
        self.assertEqual(node.fields,('id','location'))

    def test_530_503_Add_join_two_layer(self):
        """Test creation of a set of chained relations"""
        j = Join(root_model=self.modelA)
        j.addJoin('owner')
        j.addJoin('location')
        j.addJoin('owner__orders')

        joins = [ (name, node) for name, node in j.items()]

        self.assertEqual(len(joins),4)

        name, node = joins[0]
        self.assertEqual(name, 'ModelA')
        self.assertEqual(node.model, self.modelA)
        self.assertEqual(node.relation, 'ModelA')
        self.assertEqual(node.fields,())

        name, node = joins[1]
        self.assertEqual(name, 'ModelA__owner')
        self.assertEqual(node.model, self.modelB)
        self.assertEqual(node.relation, 'ModelA__owner')
        self.assertEqual(node.fields,('id','id'))

        name, node = joins[2]
        self.assertEqual(name, 'ModelA__owner__orders')
        self.assertEqual(node.model, self.modelC)
        self.assertEqual(node.relation, 'ModelA__owner__orders')
        self.assertEqual(node.fields,('orderid','id'))

        name, node = joins[3]
        self.assertEqual(name, 'ModelA__location')
        self.assertEqual(node.model, self.modelB)
        self.assertEqual(node.relation, 'ModelA__location')
        self.assertEqual(node.fields,('id','location'))

    def test_530_504_join_double_depth(self):
        """Test creation of two deep relation with one not explicitly joined"""
        j = Join(root_model=self.modelA)
        j.addJoin('owner__orders')

        joins = [(name, node) for name, node in j.items()]

        self.assertEqual(len(joins), 3)

        name, node = joins[0]
        self.assertEqual(name, 'ModelA')
        self.assertEqual(node.model, self.modelA)
        self.assertEqual(node.relation, 'ModelA')
        self.assertEqual(node.fields, ())

        name, node = joins[1]
        self.assertEqual(name, 'ModelA__owner')
        self.assertEqual(node.model, self.modelB)
        self.assertEqual(node.relation, 'ModelA__owner')
        self.assertEqual(node.fields, ('id', 'id'))

        name, node = joins[2]
        self.assertEqual(name, 'ModelA__owner__orders')
        self.assertEqual(node.model, self.modelC)
        self.assertEqual(node.relation, 'ModelA__owner__orders')
        self.assertEqual(node.fields, ('orderid', 'id'))

    def test_530_510_create_from_tuple(self):
        """Test creation of joins from tuples - single join"""
        j = Join(root_model=self.modelA)
        j.from_tuple([
            (self.modelB, 'client', 'ModelA', 'clientId','pkid', True)])
        joins = [(name, node) for name, node in j.items()]
        self.assertEqual([name for name, node in joins], ['ModelA', 'client'])
        self.assertEqual([node.model for name, node in joins], [self.modelA, self.modelB])
        self.assertEqual([node.fields for name, node in joins], [(), ('clientId','pkid')])
        self.assertEqual([node._allow_nulls for name, node in joins], [False,True])

    def test_530_511_create_double_from_tuple(self):
        """Test creation of joins from tuples - double join"""
        j = Join(root_model=self.modelA)
        j.from_tuple([
            (self.modelB, 'client', 'ModelA', 'clientId','pkid', True),
            (self.modelC, 'orders', 'client', 'pkid', 'clientId', True),
        ])
        joins = [(name, node) for name, node in j.items()]
        self.assertEqual([name for name, node in joins], ['ModelA', 'client','orders'])
        self.assertEqual([node.model for name, node in joins], [self.modelA, self.modelB, self.modelC])
        self.assertEqual([node.fields for name, node in joins], [(), ('clientId','pkid'),('pkid','clientId'),])
        self.assertEqual([node._allow_nulls for name, node in joins], [False,True,True])


class TestJoinSQL(unittest.TestCase):
    """Tests for the Join class and generation of SQL for joined tables and aliases"""

    def setUp(self):
        """Set up mock objects for testing join creation"""
        self.modelA = MagicMock(autospec=Model, name='ModelA')
        self.modelA.table_name = Mock(return_value='ModelA')

        self.modelB = MagicMock(autospec=Model, name='ModelB')
        self.modelB.table_name = Mock(return_value='ModelB')

        self.modelC = MagicMock(autospec=Model, name='ModelC')
        self.modelC.table_name = Mock(return_value='ModelC')

        def get_relationship(model_name, relationship_name):
            rels = {'modelA':{'owner':(self.modelB, 'id', 'id'),
                              'location':(self.modelB,'id','location')},
                    'modelB':{'orders':(self.modelC,'orderid','id')}
                    }
            return rels[model_name].get(relationship_name,None)

        self.modelA.get_relationship= Mock(side_effect=partial(get_relationship,'modelA'))
        self.modelB.get_relationship= Mock(side_effect=partial(get_relationship,'modelB'))

    def test_530_550_SingleTable_sql(self):
        """Test that a simple Join and the correct SQL is created"""
        j = Join(root_model=self.modelA)
        sql = j.to_sql()
        self.assertEqual(sql,'ModelA \n')

    def test_530_551_Add_join_single_child(self):
        """Test creation of a join with a relation the correct SQL is created"""
        j = Join(root_model=self.modelA)
        j.addJoin('owner')
        sql = j.to_sql()
        self.assertEqual(sql,
"""ModelA ModelA
LEFT  JOIN ModelB ModelA__owner ON ModelA.id = ModelA__owner.id
""")

    def test_530_552_Add_joins_2_children(self):
        """Test creation of two relations - both children of the main table the correct SQL is created"""
        j = Join(root_model=self.modelA)
        j.addJoin('owner', allow_nulls=True)
        j.addJoin('location',allow_nulls=True)
        sql = j.to_sql()
        self.assertEqual(sql,
"""ModelA ModelA
LEFT OUTER JOIN ModelB ModelA__owner ON ModelA.id = ModelA__owner.id
LEFT OUTER JOIN ModelB ModelA__location ON ModelA.id = ModelA__location.location
""")

    def test_530_553_Add_join_two_layer(self):
        """Test creation of a set of chained relations and correct SQL"""
        j = Join(root_model=self.modelA)
        j.addJoin('owner', allow_nulls=True)
        j.addJoin('location', allow_nulls=True)
        j.addJoin('owner__orders', allow_nulls=True)
        sql = j.to_sql()
        self.assertEqual(sql,
"""ModelA ModelA
LEFT  JOIN ModelB ModelA__owner ON ModelA.id = ModelA__owner.id
LEFT OUTER JOIN ModelC ModelA__owner__orders ON ModelA__owner.orderid = ModelA__owner__orders.id
LEFT OUTER JOIN ModelB ModelA__location ON ModelA.id = ModelA__location.location
""")

    def test_530_554_join_double_depth(self):
        """Test creation of two deep relation with one not explicitly joined and correct SQL"""
        j = Join(root_model=self.modelA)
        j.addJoin('owner__orders', allow_nulls=True)
        sql = j.to_sql()
        self.assertEqual(sql,
"""ModelA ModelA
LEFT  JOIN ModelB ModelA__owner ON ModelA.id = ModelA__owner.id
LEFT OUTER JOIN ModelC ModelA__owner__orders ON ModelA__owner.orderid = ModelA__owner__orders.id
""")

    def test_530_560_create_from_tuple(self):
        """Test creation of joins from tuples - single join & correct SQL"""
        j = Join(root_model=self.modelA)
        j.from_tuple([
            (self.modelB, 'client', 'ModelA', 'clientId','pkid', True)])
        sql = j.to_sql()
        self.assertEqual(sql,
"""ModelA ModelA
LEFT OUTER JOIN ModelB client ON ModelA.clientId = client.pkid
""")

    def test_530_511_create_double_from_tuple(self):
        """Test creation of joins from tuples - double join & correct SQL"""
        j = Join(root_model=self.modelA)
        j.from_tuple([
            (self.modelB, 'client', 'ModelA', 'clientId','pkid', True),
            (self.modelC, 'orders', 'client', 'pkid', 'clientId', True),
        ])
        sql = j.to_sql()
        self.assertEqual(sql,
"""ModelA ModelA
LEFT  JOIN ModelB client ON ModelA.clientId = client.pkid
LEFT OUTER JOIN ModelC orders ON client.pkid = orders.clientId
""")


class TestSimpleQuery(unittest.TestCase):
    #
    # Test SimpleQuery class
    #
    def setUp(self):
        pass

    def test_530_600_SimpleQuery_creation(self):
        sq = SimpleQuery()
        self.assertIsInstance(sq, FilterableQuery)
        self.assertTrue(sq.is_mutable)
        self.assertTrue(sq.is_filterable)
        self.assertTrue(sq.is_extendable)
        self.assertTrue(sq.is_limitable)
        self.assertTrue(sq.is_orderable)

    def test_530_601_SimpleQuery_creation_with_params(self):
        joins = [MagicMock(spec=Join, name='Join1')]
        test_fields = [MagicMock(spec=str, name='field1'),
                       MagicMock(spec=str, name='field2'),
                       MagicMock(spec=str, name='field2')]
        options = [MagicMock(spec=str, name='option1'),
                   MagicMock(spec=str, name='option2')]
        criteria = [MagicMock(spec=Q, name='criteria')]

        sq = SimpleQuery(joins=joins, fields=test_fields, options=options,
                         criteria=criteria)
        self.assertEqual(sq.fields, test_fields)
        self.assertEqual(sq.joins, joins)
        self.assertEqual(sq.criteria, criteria)
        self.assertEqual(sq.options, options)

    def test_530_602_SimpleQuery_from_model(self):
        model = MagicMock(autospec=Model, name='TestModel')
        model.table_name = Mock(return_value='TestModel')

        db_fields = [('a', Mock(name='a')), ('b', Mock(name='b')),
                     ('c', Mock(name='c')), ('d', Mock(name='d'))]
        for f, d in db_fields:
            d.db_column = f + '_column'

        model.db_fields = Mock(return_value=db_fields)
        model.primary_field = Mock(return_value='a')
        sq = SimpleQuery.from_model(model=model)

        self.assertEqual(sq.fields,
                         ['a_column', 'b_column', 'c_column', 'd_column'])
        self.assertEqual(len(sq.joins), 1)
        self.assertEqual(sq.joins[0].ltable.model, model)
        self.assertEqual(sq.joins[0].ltable.relation, 'TestModel')
        self.assertEqual(sq.joins[0].ltable.field, 'a')
        self.assertEqual(sq.joins[0].ltable.allow_nulls, False)
        self.assertIsNone(sq.joins[0].rtable)
        model.db_fields.assert_called_once_with()  # Could be expensive on a large model


class TestQuerySet(unittest.TestCase):
    # noinspection PyMissingOrEmptyDocstring
    def setUp(self):
        pass

    # noinspection PyMissingOrEmptyDocstring
    def tearDown(self):
        pass

    def _check_qs_clone(self, qs1, qs2, ignore=None):
        attr = {'criteria': '_criteria', 'fields': '_fields',
                'tables': '_tables', 'joins': '_joins',
                'order_by': '_order_by', 'options': '_options'}
        ignore = ignore if ignore else []

        self.assertIsNot(qs1, qs2, msg='Objects are not different')

        for name, attr_name in attr.items():
            if name in ignore:
                continue
            if getattr(qs1, attr_name) != getattr(qs2, attr_name):
                print(getattr(qs1, attr_name), getattr(qs2, attr_name))
            self.assertEqual(getattr(qs1, attr_name), getattr(qs2, attr_name),
                             msg='{} attr are different'.format(attr_name))

    def test_550_001_creation(self):
        """Creation of query set with no table_name"""
        qs = QuerySet()

        assert isinstance(qs, QuerySet)

        self.assertEqual(qs._model, None)
        self.assertEqual(qs._query, None)

    def test_550_002_creation(self):
        """Creation of query set based on models"""

        # ToDo - test with a mocked model - rather than an actual model

        # noinspection PyMissingOrEmptyDocstring
        class TestClass(Model):
            name = fields.CharField()
            birthdate = fields.DateField()

        qs = QuerySet(model=TestClass)

        self.assertCountEqual(qs._query._fields, ['id', 'name', 'birthdate'])
        self.assertEqual(qs._query._joins, [])
        self.assertEqual(qs._query._order_by, [])
        self.assertEqual(qs._query._criteria, Q())

    def test_550_003_creation(self):
        """Creation of query set based on models with overidden db_columns"""

        # ToDo - test with a mocked model - rather than an actual model

        # noinspection PyMissingOrEmptyDocstring
        class TestClass(Model):
            name = fields.CharField(db_column='artist_name')
            birthdate = fields.DateField()

        qs = QuerySet(model=TestClass)

        self.assertEqual(qs._tables, ['TestClass'])
        self.assertCountEqual(qs._fields, ['id', 'artist_name', 'birthdate'])
        self.assertEqual(qs._joins, [])
        self.assertEqual(qs._order_by, [])
        self.assertEqual(str(qs._criteria), '')

    def test_550_004_creation(self):
        """Creation of query set based on models with overidden table_name"""

        # ToDo - test with a mocked model - rather than an actual model

        # noinspection PyMissingOrEmptyDocstring
        class TestClass(Model):
            _table = 'person'
            name = fields.CharField(db_column='artist_name')
            birthdate = fields.DateField()

        qs = QuerySet(model=TestClass)

        self.assertEqual(qs._tables, ['person'])
        self.assertCountEqual(qs._fields, ['id', 'artist_name', 'birthdate'])
        self.assertEqual(qs._joins, [])
        self.assertEqual(qs._order_by, [])
        self.assertEqual(str(qs._criteria), '')

    def test_550_100_filter(self):
        """Test that filter clones the query and adds the right condition to the criteria """

        # ToDo - test with a mocked model - rather than an actual model

        # noinspection PyMissingOrEmptyDocstring
        class Person(Model):
            name = fields.CharField()
            birthdate = fields.DateField()

        qs1 = QuerySet(model=Person)

        with Invariant(qs1):
            qs2 = qs1.filter(name__exact='Tony')

        self._check_qs_clone(qs1, qs2, ignore=['criteria'])

        self.assertEqual(str(qs2._criteria), '(AND : name__exact=\'Tony\')')

    def test_550_101_filter_and_exclude(self):
        """Test that filter & exclude add the right fields to the query string"""

        # ToDo - test with a mocked model - rather than an actual model

        # noinspection PyMissingOrEmptyDocstring
        class Person(Model):
            name = fields.CharField()
            birthdate = fields.DateField()

        qs = QuerySet(model=Person)
        with Invariant(qs):
            qs1 = qs.filter(name__contains='Tony')

        with Invariant(qs1):
            qs2 = qs1.exclude(birthdate__gte=datetime.date(1960, 1, 1))

        self._check_qs_clone(qs, qs1, ignore=['criteria'])
        self._check_qs_clone(qs1, qs2, ignore=['criteria'])

        self.assertEqual(str(qs1._criteria), '(AND : name__contains=\'Tony\')')
        self.assertEqual(str(qs2._criteria),
                         '(AND : (AND : name__contains=\'Tony\'), '
                         'NOT (AND : birthdate__gte=datetime.date(1960, 1, 1)))')

    def test_550_102_order_by_and_reverse(self):
        """Test that order_by & reverse add the right entries to order_by attributes"""

        # ToDo - test with a mocked model - rather than an actual model

        # noinspection PyMissingOrEmptyDocstring
        class Person(Model):
            name = fields.CharField()
            birthdate = fields.DateField()

        qs = QuerySet(model=Person)
        with Invariant(qs):
            qs1 = qs.order_by('name', 'birthdate')

        with Invariant(qs1):
            qs2 = qs1.reverse()

        self._check_qs_clone(qs, qs1, ignore=['order_by'])
        self._check_qs_clone(qs1, qs2, ignore=['order_by'])

        self.assertEqual(qs1._order_by, ['name', 'birthdate'])
        self.assertEqual(qs2._order_by, ['-name', '-birthdate'])

    def test_550_110_annotate_count(self):
        """Test ability to annotate"""

        # ToDo - test with a mocked model - rather than an actual model

        # noinspection PyMissingOrEmptyDocstring
        class Person(Model):
            name = fields.CharField()
            birthdate = fields.DateField()

        qs1 = QuerySet(model=Person)

        with Invariant(qs1):
            qs2 = qs1.annotate(Count('name', distinct=True),
                               alias='Unique_name_count')

        self.assertIn(Annotation(Count('name', distinct=True),
                                 alias='Unique_name_count'), qs2._fields)

    def test_550_111_annotate_Sum(self):
        """Test ability to annotate"""

        # ToDo - test with a mocked model - rather than an actual model

        # noinspection PyMissingOrEmptyDocstring
        class Person(Model):
            name = fields.CharField()
            birthdate = fields.DateField()

        qs1 = QuerySet(model=Person)

        with Invariant(qs1):
            qs2 = qs1.annotate(Sum('name', distinct=True),
                               alias='Unique_name_count')

        self.assertIn(
            Annotation(Sum('name', distinct=True), alias='Unique_name_count'),
            qs2._fields)

    def test_550_112_annotate_Avg(self):
        """Test ability to annotate"""

        # ToDo - test with a mocked model - rather than an actual model

        # noinspection PyMissingOrEmptyDocstring
        class Person(Model):
            name = fields.CharField()
            birthdate = fields.DateField()

        qs1 = QuerySet(model=Person)

        with Invariant(qs1):
            qs2 = qs1.annotate(Avg('name', distinct=True),
                               alias='Unique_name_count')

        self.assertIn(
            Annotation(Avg('name', distinct=True), alias='Unique_name_count'),
            qs2._fields)

    def test_550_113_annotate_Avg(self):
        """Test ability to annotate"""

        # ToDo - test with a mocked model - rather than an actual model

        # noinspection PyMissingOrEmptyDocstring
        class Person(Model):
            name = fields.CharField()
            birthdate = fields.DateField()

        qs1 = QuerySet(model=Person)

        with Invariant(qs1):
            qs2 = qs1.annotate(Avg('name', distinct=True),
                               alias='Unique_name_count')

        self.assertIn(
            Annotation(Avg('name', distinct=True), alias='Unique_name_count'),
            qs2._fields)

    def test_550_114_annotate_Max(self):
        """Test ability to annotate"""

        # ToDo - test with a mocked model - rather than an actual model

        # noinspection PyMissingOrEmptyDocstring
        class Person(Model):
            name = fields.CharField()
            birthdate = fields.DateField()

        qs1 = QuerySet(model=Person)

        with Invariant(qs1):
            qs2 = qs1.annotate(Max('name', distinct=True),
                               alias='Unique_name_count')

        self.assertIn(
            Annotation(Max('name', distinct=True), alias='Unique_name_count'),
            qs2._fields)

    def test_550_115_annotate_Min(self):
        """Test ability to annotate"""

        # ToDo - test with a mocked model - rather than an actual model

        # noinspection PyMissingOrEmptyDocstring
        class Person(Model):
            name = fields.CharField()
            birthdate = fields.DateField()

        qs1 = QuerySet(model=Person)

        with Invariant(qs1):
            qs2 = qs1.annotate(Min('name', distinct=True),
                               alias='Unique_name_count')

        self.assertIn(
            Annotation(Min('name', distinct=True), alias='Unique_name_count'),
            qs2._fields)


# noinspection PyMissingOrEmptyDocstring
def load_tests(loader, tests=None, pattern=None):
    classes = [cls for name, cls in inspect.getmembers(sys.modules[__name__],
                                                       inspect.isclass)
               if issubclass(cls, unittest.TestCase)]

    classes.sort(key=lambda cls_: cls_.setUp.__code__.co_firstlineno)
    suite = unittest.TestSuite()
    for test_class in classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite


# noinspection PyMissingOrEmptyDocstring
@click.command()
@click.option('-v', '--verbose', default=2, help='Level of output', count=True)
@click.option('-s', '--silent', is_flag=True, default=False)
def main(verbose, silent):
    verbose = 0 if silent else verbose

    ldr = unittest.TestLoader()
    test_suite = load_tests(ldr)
    unittest.TextTestRunner(verbosity=verbose).run(test_suite)


if __name__ == '__main__':
    main()
