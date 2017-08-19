#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Test Suite for test_fields.py

Summary : 
    <summary of module/class being tested>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
    
        
Test Series 
    1nn_* : test the database fields basic functionality
        200_* : testing field default attributes
        201_* : testing expected python_type
        202_* : Test that the default values are accepted and validated
"""
import sys
import inspect
import unittest
import click
import datetime
import decimal
from pathlib import Path

from typing import Type

from repeatedtestframework import GenerateTestMethods

import pyorm.db.models.fields as fields

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '14 Aug 2017'


#
#  Wrapper to prove parameterised testing of field default field attributes
#
# noinspection PyUnusedLocal
def test_field_default_attributes_wrapper(index, field_type=None, **kwargs):
    def test_field_default_attributes_method(self):
        f = field_type()
        f.name = 'test_field'

        for method, value in kwargs.items():
            self.assertEqual(getattr(f, method)(), value,
                             msg='Unexpected value for {}'.format(method))

    return test_field_default_attributes_method


# Test that the fields have the right default settings
@GenerateTestMethods(test_name='Database_column_defaults',
                     test_method=test_field_default_attributes_wrapper,
                     test_cases=[
                         {'field_type': fields.AutoField,
                          'is_unique': True, 'is_primary': True,
                          'is_indexed': True, 'not_null': True,
                          'is_mutable': False, },
                         {'field_type': fields.BinaryField,
                          'is_unique': False, 'is_primary': False,
                          'is_indexed': False, 'not_null': False,
                          'is_mutable': True, },
                         {'field_type': fields.BooleanField,
                          'is_unique': False, 'is_primary': False,
                          'is_indexed': False, 'not_null': False,
                          'is_mutable': True, },
                         {'field_type': fields.CharField,
                          'is_unique': False, 'is_primary': False,
                          'is_indexed': False, 'not_null': False,
                          'is_mutable': True, },
                         {'field_type': fields.DateField,
                          'is_unique': False, 'is_primary': False,
                          'is_indexed': False, 'not_null': False,
                          'is_mutable': True, },
                         {'field_type': fields.DateTimeField,
                          'is_unique': False, 'is_primary': False,
                          'is_indexed': False, 'not_null': False,
                          'is_mutable': True, },
                         {'field_type': fields.DecimalField,
                          'is_unique': False, 'is_primary': False,
                          'is_indexed': False, 'not_null': False,
                          'is_mutable': True, },
                         {'field_type': fields.DurationField,
                          'is_unique': False, 'is_primary': False,
                          'is_indexed': False, 'not_null': False,
                          'is_mutable': True, },
                         {'field_type': fields.EmailField,
                          'is_unique': False, 'is_primary': False,
                          'is_indexed': False, 'not_null': False,
                          'is_mutable': True, },
                         {'field_type': fields.FileField,
                          'is_unique': False, 'is_primary': False,
                          'is_indexed': False, 'not_null': False,
                          'is_mutable': True, },
                         {'field_type': fields.FloatField,
                          'is_unique': False, 'is_primary': False,
                          'is_indexed': False, 'not_null': False,
                          'is_mutable': True, },
                         {'field_type': fields.IntegerField,
                          'is_unique': False, 'is_primary': False,
                          'is_indexed': False, 'not_null': False,
                          'is_mutable': True, },
                         {'field_type': fields.TimeField,
                          'is_unique': False, 'is_primary': False,
                          'is_indexed': False, 'not_null': False,
                          'is_mutable': True, },
                         {'field_type': fields.TimeField,
                          'is_unique': False, 'is_primary': False,
                          'is_indexed': False, 'not_null': False,
                          'is_mutable': True, },

                         # TODO - Basic features of mapping fields should be tested too.
                     ],
                     method_name_template='test_200_{index:03d}_Defaults_{test_data[field_type].__name__}',
                     method_doc_template='test Defaults for {test_data[field_type].__name__}'
                     )
class TestFieldDefaultAttributes(unittest.TestCase):
    def setUp(self):
        pass


#
# Test method wrapper for testing the python type for each field
#
# noinspection PyUnusedLocal
def test_python_type_wrapper(index, field_type=None, expected_type=None):
    def test_python_type_method(self):
        f = field_type()

        self.assertEqual(f.python_type, expected_type)

    return test_python_type_method


# Test that the fields have the right default settings
@GenerateTestMethods(test_name='Database_column_defaults',
                     test_method=test_python_type_wrapper,
                     test_cases=[
                         {'field_type': fields.AutoField,
                          'expected_type': int},
                         {'field_type': fields.BinaryField,
                          'expected_type': bytearray},
                         {'field_type': fields.BooleanField,
                          'expected_type': bool},
                         {'field_type': fields.CharField,
                          'expected_type': str},
                         {'field_type': fields.DateField,
                          'expected_type': datetime.date},
                         {'field_type': fields.DateTimeField,
                          'expected_type': datetime.datetime},
                         {'field_type': fields.DecimalField,
                          'expected_type': decimal.Decimal},
                         {'field_type': fields.DurationField,
                          'expected_type': datetime.timedelta},
                         {'field_type': fields.EmailField,
                          'expected_type': str},
                         {'field_type': fields.FileField,
                          'expected_type': Path},
                         {'field_type': fields.FloatField,
                          'expected_type': float},
                         {'field_type': fields.IntegerField,
                          'expected_type': int},
                         {'field_type': fields.TimeField,
                          'expected_type': datetime.time},

                         # TODO - Basic features of mapping fields should be tested too.
                     ],
                     method_name_template='test_201_{index:03d}_Defaults_{test_data[field_type].__name__}',
                     method_doc_template='test Defaults for {test_data[field_type].__name__}'
                     )
class TestFieldTypes(unittest.TestCase):
    def setUp(self):
        pass

# noinspection PyUnusedLocal
def test_field_default_values_wrapper(index, field_type: Type[fields._Field],
                                      default, exception=None,
                                      field_attrs=None, expected_default=None, **kwargs):
    field_attrs = field_attrs if field_attrs else {}
    expected_default = expected_default if expected_default else default

    def test_field_default_values_method_no_exception(self: unittest.TestCase):
        f = field_type(**field_attrs, default=default)
        self.assertEqual(f.default, expected_default)

    def test_field_default_values_method_exception(self: unittest.TestCase):
        with self.assertRaisesRegex(exception['class'],
                                    exception.get('regex', r'.*')):
            field_type(**field_attrs, default=default)

    return test_field_default_values_method_exception if exception else test_field_default_values_method_no_exception

@GenerateTestMethods(test_name='TestFieldDefaultValues',
                     test_method=test_field_default_values_wrapper,
                     test_cases=[
                        # Autofield
                        {'case_name': 'setting default value',
                        'field_type': fields.AutoField, 'default': 1,
                        'exception': {'class': AttributeError,
                                    'regex': r'Cannot set default value'}},

                        # Binary field default - no expected Errors
                        {'case_name':'None',
                        'field_type': fields.BinaryField, 'default': None},
                        {'case_name': 'bytestring',
                        'field_type': fields.BinaryField,
                        'default': bytearray([0, 1, 2, 3, 4, 5, 6])},
                        {'case_name': 'empty_bytestring',
                        'field_type': fields.BinaryField,
                        'default': bytearray([])},

                        # Binary field default - validation errors
                        {'case_name': 'invalid_type_int',
                        'field_type': fields.BinaryField, 'default': 3,
                        'exception': {'class': AttributeError,
                                    'regex': r'Default \'int\' value is not of expected type: expecting bytearray'}},
                        {'case_name': 'invalid_type_str',
                        'field_type': fields.BinaryField,
                        'default': 'Hello World',
                        'exception': {'class': AttributeError,
                                    'regex': r'Default \'str\' value is not of expected type: expecting bytearray'}},
                        {'case_name': 'null_false_None_default',
                        'field_type': fields.BinaryField, 'default': None,
                        'field_attrs': {'null': False},
                        'exception': {'class': AttributeError,
                                    'regex': r'Default value is None, but \'null\' attribute is False'}},

                        # Boolean field default - no expected Errors
                        {'case_name':'None',
                        'field_type': fields.BooleanField, 'default': None},
                        {'case_name': 'True',
                        'field_type': fields.BooleanField, 'default': True},
                        {'case_name': 'False',
                        'field_type': fields.BooleanField, 'default': False},

                        # Boolean field default - Validation Errors
                        {'case_name': 'null_false_None_default',
                        'field_type': fields.BooleanField, 'default': None,
                        'field_attrs': {'null': False},
                        'exception': {'class': AttributeError,
                                    'regex': r'Default value is None, but \'null\' attribute is False'}},

                        # CharField - no expected Errors
                        {'case_name': 'non_empty_string',
                        'field_type': fields.CharField,
                        'default': 'Hello_world'},
                        {'case_name': 'empty_string',
                        'field_type': fields.CharField, 'default': ''},
                        {'case_name': 'none_string',
                        'field_type': fields.CharField, 'default': None},

                        # CharField - Validation Errors
                        {'case_name': 'wrong_type',
                        'field_type': fields.CharField, 'default': 3,
                        'exception': {'class': AttributeError,
                                'regex': r'Default \'int\' value is not of expected type: expecting str'}},
                        {'case_name': 'null_false_None_default',
                        'field_type': fields.CharField, 'default': None,
                        'field_attrs': {'null': False},
                        'exception': {'class': AttributeError,
                                'regex': r'Default value is None, but \'null\' attribute is False'}},
                        {'case_name': 'too_long',
                        'field_type': fields.CharField,
                        'default': 'Hello World',
                        'field_attrs': {'max_length': 5},
                        'exception': {'class': AttributeError,
                                'regex': r'value is longer than specified max_length 5'}},
                        {'case_name': 'blank', 'field_type': fields.CharField,
                        'default': '',
                        'field_attrs': {'blank': False},
                        'exception': {'class': AttributeError,
                                'regex': r'value is blank/None but \'blank\' attribute is False'}},
                        {'case_name': 'None_blank_False',
                        'field_type': fields.CharField, 'default': None,
                        'field_attrs': {'blank': False},
                        'exception': {'class': AttributeError,
                                'regex': r'value is blank/None but \'blank\' attribute is False'}},

                        # DateField - no expected Errors
                        {'case_name': 'past date',
                        'field_type': fields.DateField,
                        'default': datetime.date(1, 1, 1)},
                        {'case_name': 'future date',
                        'field_type': fields.DateField,
                        'default': datetime.date(3000, 12, 31)},
                        {'case_name': 'None', 'field_type': fields.DateField,
                        'default': None},
                        {'case_name': 'callable',
                        'field_type': fields.DateField,
                        'default': datetime.date.today},

                        # DateField - validation Errors
                        {'case_name': 'wrong_type_int',
                        'field_type': fields.DateField, 'default': 3,
                        'exception': {'class': AttributeError,
                                    'regex': r'Default \'int\' value is not of expected type: expecting date'}},
                        {'case_name': 'wrong_type_str_',
                        'field_type': fields.DateField,
                        'default': 'Hello World',
                        'exception': {'class': AttributeError,
                                    'regex': r'Default \'str\' value is not of expected type: expecting date'}},
                        {'case_name': 'null_false_None_default',
                        'field_type': fields.DateField, 'default': None,
                        'field_attrs': {'null': False},
                        'exception': {'class': AttributeError,
                                    'regex': r'Default value is None, but \'null\' attribute is False'}},

                        # DateTime - no expected Errors
                        {'case_name': 'past_date', 'field_type': fields.DateTimeField,
                            'default': datetime.datetime(1, 1, 1, 0, 0, 1)},
                        {'case_name': 'future_date', 'field_type': fields.DateTimeField,
                            'default': datetime.datetime(3000, 12, 31, 23, 59, 59)},
                        {'case_name': 'None', 'field_type': fields.DateField,
                            'default': None},
                        {'case_name': 'callable', 'field_type': fields.DateTimeField,
                            'default': datetime.datetime.now},

                        # DateField - validation Errors
                        {'case_name': 'wrong_type_int',
                        'field_type': fields.DateTimeField, 'default': 3,
                        'exception': {'class': AttributeError,
                                    'regex': r'Default \'int\' value is not of expected type: expecting datetime'}},
                        {'case_name': 'wrong_type_str_',
                        'field_type': fields.DateTimeField,
                        'default': 'Hello World',
                        'exception': {'class': AttributeError,
                                    'regex': r'Default \'str\' value is not of expected type: expecting datetime'}},
                        {'case_name': 'null_false_None_default',
                        'field_type': fields.DateTimeField, 'default': None,
                        'field_attrs': {'null': False},
                        'exception': {'class': AttributeError,
                                    'regex': r'Default value is None, but \'null\' attribute is False'}},

                        # Decimal field - no expected Errors
                        {'case_name': 'Integer_Decimal', 'field_type': fields.DecimalField,
                            'default': decimal.Decimal(1)},
                        {'case_name': 'non_Integer_Decimal', 'field_type': fields.DecimalField,
                            'default': decimal.Decimal(1.7)},
                        {'case_name': 'negative_non_Integer_Decimal', 'field_type': fields.DecimalField,
                           'default': decimal.Decimal(-17.3)},
                        {'case_name': 'Integer', 'field_type': fields.DecimalField, 'default': 1,
                          'expected_default': decimal.Decimal("1")},
                        {'case_name': 'float', 'field_type': fields.DecimalField, 'default': 1.3,
                           'expected_default': decimal.Decimal(1.3)},
                        {'case_name': 'tuple', 'field_type': fields.DecimalField,'default': (0, (0, 1, 1, 4), -3),
                            'expected_default': decimal.Decimal('0.114')},
                        {'case_name': 'str', 'field_type': fields.DecimalField, 'default': '0.0117',
                            'expected_default': decimal.Decimal('0.0117')},

                        # Decimal field Exception errors
                        {'case_name': 'Invalid_String',
                        'field_type': fields.DecimalField,
                        'default': 'Hello World',
                        'exception': {'class': AttributeError,
                                    'regex': r'Unable to convert str to decimal : Invalid syntax'}, },
                        {'case_name': 'Invalid_tuple',
                        'field_type': fields.DecimalField,
                        'default': (0, 0, 0),
                        'exception': {'class': AttributeError,
                                    'regex': r'Unable to convert tuple to decimal : Invalid syntax'}, },
                         {'case_name': 'Invalid_value',
                          'field_type': fields.DecimalField,
                          'default': 3+4.5j,
                          'exception': {'class': AttributeError,
                                        'regex': r'Unable to convert complex to decimal : Invalid syntax'}, },
                        {'case_name': 'null_false_None_default',
                        'field_type': fields.DecimalField, 'default': None,
                        'field_attrs': {'null': False},
                        'exception': {'class': AttributeError,
                                    'regex': r'Default value is None, but \'null\' attribute is False'}, },

                        # Duration field - no expected Errors
                        {'case_name': 'positive_time_delta', 'field_type': fields.DurationField,
                            'default': datetime.timedelta(352)},
                        {'case_name': 'negative_time_delta', 'field_type': fields.DurationField,
                            'default': datetime.timedelta(-352)},
                        {'case_name': 'zero_time_delta', 'field_type': fields.DurationField,
                            'default': datetime.timedelta(0)},
                        {'case_name': 'None','field_type': fields.DurationField,
                            'default': None},

                        # Duration field - validation errors
                        {'case_name': 'null_false_None_default', 'field_type': fields.DurationField, 'default': None,
                            'field_attrs': {'null': False},
                            'exception': {'class': AttributeError,
                                    'regex': r'Default value is None, but \'null\' attribute is False'}},

                        # Email Field - no errors
                        {'case_name': 'vaild_email','field_type': fields.EmailField, 'default': 'a.b@c.com'},
                        {'case_name': 'empty_string','field_type': fields.EmailField, 'default': ''},
                        {'case_name': 'None', 'field_type': fields.EmailField, 'default': None},

                        # Email Field - validation errors
                        {'case_name': 'invalid_email', 'field_type': fields.EmailField, 'default': 'tony@com',
                        'exception': {'class': AttributeError,
                                    'regex': r'Invalid Default value : Invalid Email address'}},
                        {'case_name': 'None_null_false', 'field_type': fields.EmailField, 'default': None,
                            'field_attrs': {'null': False},
                            'exception': {'class': AttributeError,
                                    'regex': r'Default value is None, but \'null\' attribute is False'}},
                        {'case_name': 'empty_blank_False', 'field_type': fields.EmailField, 'default': '',
                            'field_attrs': {'blank': False},
                            'exception': {'class': AttributeError,
                                    'regex': r'value is blank/None but \'blank\' attribute is False'}},
                        {'case_name': 'None_blank_False', 'field_type': fields.EmailField, 'default': None,
                            'field_attrs': {'blank': False},
                            'exception': {'class': AttributeError,
                                    'regex': r'value is blank/None but \'blank\' attribute is False'}},

                        #TODO test Filefield once field semantics are understood

                        # Floating Point numbers - no errors expected
                        {'case_name':'floating_point_value', 'field_type':fields.FloatField, 'default':3.7},
                        {'case_name':'integer_value', 'field_type': fields.FloatField, 'default': 3, 'expected_default':3.0},
                        {'case_name': 'string_value','field_type': fields.FloatField, 'default': '17.5', 'expected_default': 17.5},
                        {'case_name': 'negative_string_value','field_type': fields.FloatField, 'default': '-0.9', 'expected_default': -0.9},

                        # Floating Point numbers - errors
                        {'case_name': 'floating_point_value', 'field_type': fields.FloatField, 'default': 3.0+0.1j,
                            'exception':{'class':AttributeError,
                                         'regex':r'Invalid value : can\'t convert complex to float'}},
                        {'case_name': 'honour_not_null', 'field_type': fields.FloatField, 'default': None,
                            'field_attrs':{'null':False},
                            'exception':{'class':AttributeError,
                                         'regex':r'Default value is None, but \'null\' attribute is False'}},

                        # ToDo tests for 'ForeignKey'

                        # Tests for IntegerField - no errors expected
                        {'case_name':'integer_value', 'field_type': fields.IntegerField, 'default': 3, 'expected_default':3},
                        {'case_name':'floating_point_value', 'field_type':fields.IntegerField, 'default':3.7,'expected_default':3},
                        {'case_name': 'string_value','field_type': fields.IntegerField, 'default': '17', 'expected_default': 17},
                        {'case_name': 'negative_string_value','field_type': fields.IntegerField, 'default': '-3', 'expected_default': -3},

                        # Tests for Integerfield - expected errors
                        {'case_name': 'invalid_string', 'field_type': fields.IntegerField, 'default': '-3.9',
                            'exception':{'class':AttributeError,
                                         'regex':r"Invalid value : invalid literal for int\(\) with base 10: '-3.9'"}},
                        {'case_name': 'invalid_string','field_type': fields.IntegerField, 'default': '3Hello',
                              'exception': {'class': AttributeError,
                                        'regex': r"Invalid value : invalid literal for int\(\) with base 10: '3Hello'"}},
                        {'case_name': 'honouring_null','field_type': fields.IntegerField, 'default': '3Hello',
                              'field_attr':{'null':True},
                              'exception': {'class': AttributeError,
                                        'regex': r"Invalid value : invalid literal for int\(\) with base 10: '3Hello'"}},
                        #
                        # ToDo'Tests for TimeField'

                     ],
                     method_name_template='test_202_{index:03d}_Defaults_{test_data[field_type].__name__}_{test_data[case_name]}',
                     method_doc_template='test Defaults for {test_data[field_type].__name__} {test_data[case_name]}'
                     )
class TestFieldDefaultValues(unittest.TestCase):
    def setUp(self):
        pass



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

# noinspection PyUnusedLocal
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
