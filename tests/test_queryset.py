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
    530 - OrderingAndLimits, FilterableQuery, RawSQL
    540 - Combinations
    550 - Query
    560 - Query Sets
    
"""

# Todo Tests 500, 520, 530,540,550,560
import sys

import unittest
import click
import inspect

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '27 Aug 2017'

from pyorm.db.models.queryset import F,Q,BaseQuery, OrderingAndLimits, QuerySet, FilterableQuery, Difference, Union,Intersection

from pyorm.db.models.models import Model
import pyorm.db.models.fields as fields
import pyorm.core.exceptions as exceptions

from pyorm.db.models.utils import Annotation
from pyorm.db.models.aggregates import Count, Sum, Avg, Max, Min

from tests.DummyEngine import DummyEngine, MockedEngine
import decimal
import datetime

from copy import copy


class Invariant():
    def __init__(self, obj):
        """Conext manager to confirm that an object doesn't change within that context

           Confirms that the each attribute is bound to the same value or to a object which tests equal
           this is a shallow comparison only - it doesn't test attributes of attrributes.
        """
        self._obj = obj
        self._old_obj = copy(obj)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            return False

        for att in self._obj.__dict__:
            if getattr(self._obj, att) == getattr(self._old_obj, att):
                continue
            else:
                raise ValueError(
                    '{name} attribute is different : \noriginal : {original!r}\n     now : {now!r}'.format(
                        name=att, now=getattr(self._obj, att),
                        original=getattr(self._old_obj, att))) from None


# ToDo Test Looks generate the right SQL and tables

class TestQ(unittest.TestCase):
    def setUp(self):
        pass

    def test_510_000_empty_Q(self):
        q = Q()
        print(q)
        self.assertEqual(q,Q())

    def test_510_001_simpleQ(self):
        """Test for the creation of a simple Q class - needed for next tests on empty Q"""
        q = Q(table_field__lte=17)
        self.assertEqual(str(q), '(AND : table_field__lte=17)')

    def test_510_002_empty_Q_and(self):
        q = Q()
        q1 = q & Q(test_name=17)
        self.assertEqual(q1,Q(test_name=17))

    def test_510_003_empty_Q_or(self):
        q = Q()
        q1 = q | Q(test_name=17)
        self.assertEqual(q1,Q(test_name=17))

    def test_510_004_empty_Q_and(self):
        q = Q()
        q1 = Q(test_name=17) & q
        self.assertEqual(q1,Q(test_name=17))

    def test_510_005_empty_Q_or(self):
        q = Q()
        q1 = Q(test_name=17) | q
        self.assertEqual(q1,Q(test_name=17))

    def test_510_007_negated_simpleQ(self):
        """Test a negated Q class"""
        q = Q(table_field__lte=17)
        self.assertEqual(str(~q), 'NOT (AND : table_field__lte=17)')

    def test_510_103_two_argumentQ(self):
        q = Q(table_field__lte=17, table_section_gte=23)
        self.assertEqual(str(q),
                         '(AND : table_field__lte=17, table_section_gte=23)')

    def test_510_104_two_argumentQ_string(self):
        q = Q(table_field__iexact='hello', table_section_gte=23)
        self.assertEqual(str(q),
                         '(AND : table_field__iexact=\'hello\', table_section_gte=23)')

    def test_510_105_two_argumentQ_decimal(self):
        q = Q(table_field__iexact=decimal.Decimal('17.357'),
                       table_section_gte=23)
        self.assertEqual(str(q),
                         '(AND : table_field__iexact=Decimal(\'17.357\'), table_section_gte=23)')

    def test_510_106_two_argumentQ_date(self):
        q = Q(
            table_field__iexact=datetime.date(year=2011, month=8, day=13),
            table_section_gte=23)
        self.assertEqual(str(q),
                         '(AND : table_field__iexact=datetime.date(2011, 8, 13), table_section_gte=23)')

    def test_510_107_two_argumentQ_datetime(self):
        q = Q(
            table_field__iexact=datetime.datetime(year=2011, month=8, day=13,
                                                  hour=13, minute=35,
                                                  second=45, microsecond=450),
            table_section_gte=23)
        self.assertEqual(str(q),
                         '(AND : table_field__iexact=datetime.datetime(2011, 8, 13, 13, 35, 45, 450), table_section_gte=23)')

    def test_510_108_two_argumentQ_timedelta(self):
        q = Q(
            table_field__iexact=datetime.timedelta(days=173, seconds=543,
                                                   microseconds=947),
            table_section_gte=23)
        self.assertEqual(str(q),
                         '(AND : table_field__iexact=datetime.timedelta(173, 543, 947), table_section_gte=23)')

    def test_510_200_two_anded_together(self):
        q1 = Q(table_field_lte=17)
        q2 = Q(table_section_gte=18)
        q3 = q1 & q2
        self.assertEqual(str(q3),
                         '(AND : (AND : table_field_lte=17), (AND : table_section_gte=18))')

    def test_510_101_two_ored_together(self):
        q1 = Q(table_field_lte=17)
        q2 = Q(table_section_gte=18)
        q3 = q1 | q2
        self.assertEqual(str(q3),
                         '(OR : (AND : table_field_lte=17), (AND : table_section_gte=18))')

    def test_510_102_two_anded_together_one_negated(self):
        q1 = Q(table_field_lte=17)
        q2 = Q(table_section_gte=18)
        q3 = q1 | ~q2
        self.assertEqual(str(q3),
                         '(OR : (AND : table_field_lte=17), NOT (AND : table_section_gte=18))')

    def test_510_103_two_anded_together_both_negated(self):
        q1 = Q(table_field_lte=17)
        q2 = Q(table_section_gte=18)
        q3 = ~q1 | ~q2
        self.assertEqual(str(q3),
                         '(OR : NOT (AND : table_field_lte=17), NOT (AND : table_section_gte=18))')


# ToDO that Q objects create the correct SQL AND the correct tables etc

class TestF(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_520_000_basic_F_object(self):
        f = F('test__name')
        self.assertEqual(F('test__name'), f)

    def test_520_001_basic_negation(self):
        f = F('test__name')
        f = -f
        self.assertIsNotNone(f)
        self.assertEqual(-F('test__name'), f)

    def test_520_010_basic_Addition(self):
        f = F('test__name')
        f = f + 10
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') + 10, f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, 10)
        self.assertEqual(f._operator, '+')

    def test_520_011_basic_Subtraction(self):
        f = F('test__name')
        f = f - 10
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') - 10, f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, 10)
        self.assertEqual(f._operator, '-')

    def test_520_012_basic_Multi(self):
        f = F('test__name')
        f = f * 10
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') * 10, f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, 10)
        self.assertEqual(f._operator, '*')

    def test_520_013_basic_Division(self):
        f = F('test__name')
        f = f / 10
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') / 10, f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, 10)
        self.assertEqual(f._operator, '/')

    def test_520_014_basic_lshift(self):
        f = F('test__name')
        f = f << 10
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') << 10, f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, 10)
        self.assertEqual(f._operator, '<<')

    def test_520_015_basic_rshift(self):
        f = F('test__name')
        f = f >> 10
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') >> 10, f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, 10)
        self.assertEqual(f._operator, '>>')

    def test_520_016_basic_xor(self):
        f = F('test__name')
        f = f ^ 10
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') ^ 10, f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, 10)
        self.assertEqual(f._operator, '^')

    def test_520_017_basic_and(self):
        f = F('test__name')
        f = f & 10
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') & 10, f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, 10)
        self.assertEqual(f._operator, '&')

    def test_520_018_basic_or(self):
        f = F('test__name')
        f = f | 10
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') | 10, f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, 10)
        self.assertEqual(f._operator, '|')

    def test_520_019_basic_mod(self):
        f = F('test__name')
        f = f % 10
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') % 10, f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, 10)
        self.assertEqual(f._operator, '%')

    def test_520_050_basic_Addition(self):
        f = F('test__name')
        f = f + F('test__group')
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') + F('test__group'), f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, F('test__group'))
        self.assertEqual(f._operator, '+')

    def test_520_051_basic_Subtraction(self):
        f = F('test__name')
        f = f - F('test__group')
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') - F('test__group'), f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, F('test__group'))
        self.assertEqual(f._operator, '-')

    def test_520_052_basic_Multi(self):
        f = F('test__name')
        f = f * F('test__group')
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') * F('test__group'), f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, F('test__group'))
        self.assertEqual(f._operator, '*')

    def test_520_053_basic_Division(self):
        f = F('test__name')
        f = f / F('test__group')
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') / F('test__group'), f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, F('test__group'))
        self.assertEqual(f._operator, '/')

    def test_520_054_basic_lshift(self):
        f = F('test__name')
        f = f << F('test__group')
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') << F('test__group'), f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, F('test__group'))
        self.assertEqual(f._operator, '<<')

    def test_520_055_basic_rshift(self):
        f = F('test__name')
        f = f >> F('test__group')
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') >> F('test__group'), f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, F('test__group'))
        self.assertEqual(f._operator, '>>')

    def test_520_056_basic_xor(self):
        f = F('test__name')
        f = f ^ F('test__group')
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') ^ F('test__group'), f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, F('test__group'))
        self.assertEqual(f._operator, '^')

    def test_520_057_basic_and(self):
        f = F('test__name')
        f = f & F('test__group')
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') & F('test__group'), f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, F('test__group'))
        self.assertEqual(f._operator, '&')

    def test_520_058_basic_or(self):
        f = F('test__name')
        f = f | F('test__group')
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') | F('test__group'), f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, F('test__group'))
        self.assertEqual(f._operator, '|')

    def test_520_059_basic_mod(self):
        f = F('test__name')
        f = f % F('test__group')
        self.assertIsNotNone(f)
        self.assertEqual(F('test__name') % F('test__group'), f)
        self.assertEqual(f._lhs, F('test__name'))
        self.assertEqual(f._rhs, F('test__group'))
        self.assertEqual(f._operator, '%')
        
    def test_520_070_Combing_terms_addition_with_brackets(self):
        f = (F('x') + F('y')) * F('z')
        self.assertIsNotNone(f)
        self.assertEqual((F('x') + F('y')) * F('z'),f)
        self.assertEqual(f._lhs, (F('x') + F('y')))
        self.assertEqual(f._rhs,  F('z'))
        self.assertEqual(f._operator, '*')

    def test_520_071_Combing_terms_multiplication_with_addition(self):
        f = F('x') * F('y') + F('z')
        self.assertIsNotNone(f)
        self.assertEqual((F('x') * F('y')) + F('z'),f)
        self.assertEqual(f._lhs, (F('x') * F('y')))
        self.assertEqual(f._rhs,  F('z'))
        self.assertEqual(f._operator, '+')

    def test_520_072_negation_of_combined_exp(self):
        f = F('x') + F('y')
        self.assertIsNotNone(f)
        f = -f
        self.assertIsNotNone(f)
        self.assertEqual(f,-(F('x')+F('y')))

class TestQueryHierarchy(unittest.TestCase):
    """ Test the various classes within the Query Heirarchy

        tests 530
            000 to 099 - BaseQuery
            100 to 199 - OrderingAndLimits
            200 to 299 - FilterableQuery
            300 to 399 - RawSQL
            400 to 499 - Combination (and Union, Intersect & Difference)
            500 to 599 - SimpleQuery
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_530_000_BaseQuery_Creation(self):
        bq = BaseQuery()
        self.assertTrue(bq.is_mutable)
        self.assertTrue(bq.is_extendable)
        self.assertTrue(bq.is_filterable)
        self.assertTrue(bq.is_orderable)
        self.assertTrue(bq.is_limitable)

    def test_530_001_BaseQuery_Creation_Immuatble(self):
        bq = BaseQuery(mutable=False)
        self.assertFalse(bq.is_mutable)
        self.assertFalse(bq.is_extendable)
        self.assertFalse(bq.is_filterable)
        self.assertFalse(bq.is_orderable)
        self.assertFalse(bq.is_limitable)

    def test_530_010_BaseQuery_Creation_Immuatble_overides_extendable(self):
        bq = BaseQuery(mutable=False, extendable=True)
        self.assertFalse(bq.is_mutable)
        self.assertFalse(bq.is_extendable)
        self.assertFalse(bq.is_filterable)
        self.assertFalse(bq.is_orderable)
        self.assertFalse(bq.is_limitable)

    def test_530_021_BaseQuery_Creation_Immuatble_overides_filterable(self):
        bq = BaseQuery(mutable=False, filterable=True)
        self.assertFalse(bq.is_mutable)
        self.assertFalse(bq.is_extendable)
        self.assertFalse(bq.is_filterable)
        self.assertFalse(bq.is_orderable)
        self.assertFalse(bq.is_limitable)

    def test_530_022_BaseQuery_Creation_Immuatble_overides_orderable(self):
        bq = BaseQuery(mutable=False, orderable=True)
        self.assertFalse(bq.is_mutable)
        self.assertFalse(bq.is_extendable)
        self.assertFalse(bq.is_filterable)
        self.assertFalse(bq.is_orderable)
        self.assertFalse(bq.is_limitable)

    def test_530_023_BaseQuery_Creation_Immuatble_overides_limitable(self):
        bq = BaseQuery(mutable=False, limitable=True)
        self.assertFalse(bq.is_mutable)
        self.assertFalse(bq.is_extendable)
        self.assertFalse(bq.is_filterable)
        self.assertFalse(bq.is_orderable)
        self.assertFalse(bq.is_limitable)

    def test_530_030_BaseQuery_Creation_Mutable_and_not_extendable(self):
        bq = BaseQuery(extendable=False)
        self.assertTrue(bq.is_mutable)
        self.assertFalse(bq.is_extendable)
        self.assertTrue(bq.is_filterable)
        self.assertTrue(bq.is_orderable)
        self.assertTrue(bq.is_limitable)

    def test_530_031_BaseQuery_Creation_Mutable_and_not_filterable(self):
        bq = BaseQuery(filterable=False)
        self.assertTrue(bq.is_mutable)
        self.assertTrue(bq.is_extendable)
        self.assertFalse(bq.is_filterable)
        self.assertTrue(bq.is_orderable)
        self.assertTrue(bq.is_limitable)

    def test_530_030_BaseQuery_Creation_Mutable_and_not_orderable(self):
        bq = BaseQuery(orderable=False)
        self.assertTrue(bq.is_mutable)
        self.assertTrue(bq.is_extendable)
        self.assertTrue(bq.is_filterable)
        self.assertFalse(bq.is_orderable)
        self.assertTrue(bq.is_limitable)

    def test_530_030_BaseQuery_Creation_Mutable_and_not_limitable(self):
        bq = BaseQuery(limitable=False)
        self.assertTrue(bq.is_mutable)
        self.assertTrue(bq.is_extendable)
        self.assertTrue(bq.is_filterable)
        self.assertTrue(bq.is_orderable)
        self.assertFalse(bq.is_limitable)

    #
    # Testing Ordering & Limits class
    #

    def test_530_100_OrderingAndLimits_Creation(self):
        a = OrderingAndLimits()
        self.assertEqual(a.order_by, [])
        self.assertEqual(a.limits, [])
        self.assertTrue(a.is_limitable)
        self.assertTrue(a.is_orderable)

    def test_530_100a_OrderingAndLimits_Creation_Passthrough(self):
        b = OrderingAndLimits(extendable=False, filterable=False)
        self.assertFalse(a.is_extendable)
        self.assertFalse(a.is_filterable)
        self.assertTrue(a.is_limitable)
        self.assertTrue(a.is_orderable)

    def test_530_101_OrderingAndLimits_adding_ordering(self):
        a = OrderingAndLimits()
        a.add_order_by('test__name')
        self.assertEqual(a.order_by, ['test__name'])
        self.assertEqual(a.limits, [])

    def test_530_102_OrderingAndLimits_adding_ordering_F_object(self):
        a = OrderingAndLimits()
        a.add_order_by(F('test__name'))
        self.assertEqual(a.order_by, [F('test__name')])
        self.assertEqual(a.limits, [])

    def test_530_103_OrderingAndLimits_adding_ordering_F_object(self):
        a = OrderingAndLimits()
        a.add_order_by(F('test__name') + 1, 'test__x')
        self.assertEqual(a.order_by, [F('test__name') + 1, 'test__x'])
        self.assertEqual(a.limits, [])

    def test_530_104_OrderingAndLimits_inverting_with_Complex_object(self):
        a = OrderingAndLimits()
        a.add_order_by(F('test__name') + 1, 'test__x')
        a.invert_ordering()
        self.assertEqual(a.order_by,
                         [-(F('test__name') + 1), '-test__x'])
        self.assertEqual(a.limits, [])

    def test_530_104_OrderingAndLimits_Limits(self):
        a = OrderingAndLimits()
        a.add_limits(F('test_name'))
        self.assertIsInstance(a.limits[0], F)
        self.assertEqual(a.limits, [F('test_name')])

    def test_530_105_OrderingAndLimits_Limits_TwoArgs(self):
        a = OrderingAndLimits()
        a.add_limits(F('test_name'),25)
        self.assertIsInstance(a.limits[0], F)
        self.assertEqual(a.limits, [F('test_name'),25])

    def test_530_106_OrderingAndLimits_Limits_ThreeArgs(self):
        a = OrderingAndLimits()
        with self.assertRaises(exceptions.LimitsError):
            a.add_limits(F('test_name'),25, 18)

    def test_530_107_clear_limits(self):
        a = OrderingAndLimits()
        a.add_limits(F('test_name'),25)
        self.assertEqual(a.limits, [F('test_name'),25])
        a.clear_limits()
        self.assertEqual(a.limits, [])

    def test_530_200_FilterableQuery(self):
        fq = FilterableQuery()
        self.assertIsInstance(fq, OrderingAndLimits)
        self.assertEqual(fq.criteria, Q())

    def test_530_201_FilterableQuery_set_criteria(self):
        fq = FilterableQuery()
        fq.criteria &= Q(test_name=17)
        self.assertIsInstance(fq, OrderingAndLimits)
        self.assertEqual(fq.criteria, Q(test_name=17))

    def test_530_202_FilterableQuery_set_complex(self):
        fq = FilterableQuery()
        fq.criteria &= Q(test_name=17) | Q(test_name=16)
        self.assertIsInstance(fq, OrderingAndLimits)
        self.assertEqual(fq.criteria, Q(test_name=17) | Q(test_name=16))

class TestQuerySet(unittest.TestCase):
    def setUp(self):
        pass

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
        """Creation of query set with no model"""
        qs = QuerySet()

        assert isinstance(qs, QuerySet)

        self.assertEqual(qs._tables, [])
        self.assertEqual(qs._fields, [])
        self.assertEqual(qs._joins, [])
        self.assertEqual(qs._order_by, [])
        self.assertEqual(str(qs._criteria), '')

    def test_550_002_creation(self):
        """Creation of query set based on models"""

        class TestClass(Model):
            name = fields.CharField()
            birthdate = fields.DateField()

        qs = QuerySet(model=TestClass)

        self.assertEqual(qs._tables, ['TestClass'])
        self.assertCountEqual(qs._fields, ['id', 'name', 'birthdate'])
        self.assertEqual(qs._joins, [])
        self.assertEqual(qs._order_by, [])
        self.assertEqual(str(qs._criteria), '')

    def test_550_003_creation(self):
        """Creation of query set based on models with overidden db_columns"""

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
