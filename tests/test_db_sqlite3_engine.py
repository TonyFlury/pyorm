#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Test Suite for test_db_engine.py

Summary : 
    <summary of module/class being tested>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
    
Test Series 
    3**_*** : test sqlite db engine
    
"""
import sys
import unittest
import click
import inspect
from pathlib import Path

import re
import datetime

from TempDirectoryContext import TempDirectoryContext as TDC

from pyorm.db.engine.sqlite import Engine, Constants

from pyorm.db.models.fields import CharField, AutoField, IntegerField, DateField, DateTimeField, EmailField, BooleanField
from repeatedtestframework import GenerateTestMethods

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '29 Jul 2017'


class TestCaeExt(unittest.TestCase):
    def assertRegexSearch(self:unittest.TestCase, text, regex, msg=None):
        msg = msg + '\ntext: {text}\nregex: {regex}\n' if msg else 'regex not found in:\n{text}\n{regex}'
        if not re.search(regex,text):
            raise self.failureException(msg.format(text=text,regex=regex))

    def assertNotRegexSearch(self:unittest.TestCase, text, regex, msg=None):
        msg = msg + '\ntext: {text}\nregex: {regex}\n' if msg else 'regex not found in:\n{text}\n{regex}'
        msg = msg if msg else 'regex found in:\n{text}\n{regex}'
        if re.search(regex,text):
            raise self.failureException(msg.format(text=text,regex=regex))


class Database(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_400_000_non_existant_db(self):
        """test that db is created if it doesn't exist"""
        with TDC() as temp_dir:
            file = Path(temp_dir) / 'database.db'
            self.assertFalse(file.exists(),'Database file exists pre test')
            eng = Engine(file)
            eng.start()
            self.assertTrue(file.exists(), 'Database file does not exists post test')


#
#  Wrapper to provide parameterised testing of column names
#
def db_column_test_name_wrapper(index, **kwargs):
    def db_column_test_name(self):
        f = kwargs['field_type']( db_column=kwargs['db_column'])
        f.name = kwargs['field_name']

        segment = Engine.column_name(field=f)
        self.assertEqual(segment, '\"'+kwargs['expected']+'\"')
    return db_column_test_name

#
#  Wrapper to provide parameterised testing of field types
#
def db_column_test_type_wrapper(index,**kwargs):
    def db_column_test_type(self):
        f = kwargs['field_type']()
        f.name = 'test_field'

        segment = Engine.column_type(field=f)
        self.assertEqual(segment, kwargs['expected'])
    return db_column_test_type


# TODO Make sure every field is tested - several missing as currently

# Test that db column names are created correctly
@GenerateTestMethods(test_name = 'Database_column_name_tests',
                     test_method=db_column_test_name_wrapper,
                     test_cases=[
                         { 'summary':'db_column not provided',
                                        'field_type':CharField, 'field_name':'test', 'db_column':None, 'expected':'test'},
                         {'summary': 'db_column same as name',
                                      'field_type': CharField, 'field_name': 'test',
                                          'db_column': 'test', 'expected': 'test'},
                         {'summary': 'db_column different to name',
                                      'field_type': CharField, 'field_name': 'test',
                                          'db_column': 'test2', 'expected': 'test2'},

                         {'summary': 'db_column not provided',
                          'field_type': AutoField, 'field_name': 'id',
                          'db_column': None, 'expected': 'id'},
                         {'summary': 'db_column provided',
                          'field_type': AutoField, 'field_name': 'id',
                          'db_column': 'pkid', 'expected': 'pkid'},

                         {'summary': 'db_column not provided',
                          'field_type': IntegerField, 'field_name': 'id',
                          'db_column': None, 'expected': 'id'},
                         {'summary': 'db_column provided',
                          'field_type': IntegerField, 'field_name': 'id',
                          'db_column': 'pkid', 'expected': 'pkid'},

                         {'summary': 'db_column not provided',
                          'field_type': DateField, 'field_name': 'id',
                          'db_column': None, 'expected': 'id'},
                         {'summary': 'db_column provided',
                          'field_type': DateField, 'field_name': 'id',
                          'db_column': 'pkid', 'expected': 'pkid'},

                         {'summary': 'db_column not provided',
                          'field_type': DateTimeField, 'field_name': 'id',
                          'db_column': None, 'expected': 'id'},
                         {'summary': 'db_column provided',
                          'field_type': DateTimeField, 'field_name': 'id',
                          'db_column': 'pkid', 'expected': 'pkid'},

                         {'summary': 'db_column not provided',
                          'field_type': EmailField, 'field_name': 'id',
                          'db_column': None, 'expected': 'id'},
                         {'summary': 'db_column provided',
                          'field_type': EmailField, 'field_name': 'id',
                          'db_column': 'pkid', 'expected': 'pkid'},

                         {'summary': 'db_column not provided',
                          'field_type': BooleanField, 'field_name': 'id',
                          'db_column': None, 'expected': 'id'},
                         {'summary': 'db_column provided',
                          'field_type': BooleanField, 'field_name': 'id',
                          'db_column': 'pkid', 'expected': 'pkid'},

                     ],
                     method_name_template='test_400_{index:03d}_{test_data[field_type].__name__}',
                     method_doc_template='test {test_data[field_type].__name__}: {test_data[summary]}'
                     )
# Test that Fields have the right DB column types
@GenerateTestMethods(test_name = 'Database_column_type_tests',
                     test_method=db_column_test_type_wrapper,
                     test_cases=[
                         {'field_type':CharField, 'expected':'text'},
                         {'field_type': AutoField, 'expected': 'integer'},
                         {'field_type': IntegerField, 'expected': 'integer'},
                         {'field_type': DateField, 'expected':'datetime'},
                         {'field_type': DateTimeField, 'expected': 'datetime'},
                         {'field_type': EmailField, 'expected': 'text'},
                         {'field_type': BooleanField, 'expected': 'boolean'}
                     ],

                     method_name_template='test_410_{index:03d}_{test_data[field_type].__name__}',
                     method_doc_template='test {test_data[field_type].__name__}'
                     )

class DBColumnNames(TestCaeExt):
    def setUp(self):
        pass

#
# Wrapper method for testing constraints
#
def test_constraint_wrapper(index, case_name='', field_type=None,**kwargs) :
    """Wrapper for constraint test methods - returns a method which is closed over the arguments """
    # Regexs to be expeected when certain parameters are passed
    # Dictionary - key is the keyword arguemnt name
    #              Value is a 2-tuple (flag_callable, regex)
    #              flag_callable is called with value of keyword arguent
    #                       callable should returns True if regex should be matched
    constraint_regex = {'unique':(lambda x: x.is_unique() and not x.is_primary(), r'UNIQUE'),
                        'null': (lambda x: x.not_null() and not x.is_primary(), r'NOT\s+NULL'),
                        'max_length': ( lambda x : hasattr(x,'max_length') and x.max_length is not None and x.max_length != Constants['MAX_TEXT_LENGTH'],
                                       r'CHECK\s+\(\s*typeof\(\"{name}\"\)\s+=\s+\"{type}\"\s+and\s+length\(\"{name}\"\)\s+<=\s+{length}\s*\)'.format(
                                           type=Engine.column_type(field=field_type(**kwargs)),
                                           name='test_field',
                                           length=kwargs.get('max_length',None))
                                       ),
                        'primary':(lambda x: x.is_primary(),r'PRIMARY KEY')
                        }



    def test_constraint_method(self:TestCaeExt):
        """Test that the expected constraints are actually provided."""
        f = field_type(**kwargs)
        f.name = 'test_field'

        # get a list of the regex's expected based on the parameters
        regex = [(kw, check[1]) for kw, check in constraint_regex.items() if check[0](f)]

        # get a list of the constraints that are generated
        constraints = list(c for c in Engine.column_constraint(field=f))

        # Identify any constraints that fail to match all the regex's
        missed_constraints = [c for c in constraints if all( not re.match(r[1],c) for r in regex)]

        # Identify any regex that fail to be matched by any constraint
        missed_regex = [r[0] for r in regex if all( not re.match(r[1],c) for c in constraints)]

        self.assertEqual(missed_constraints, [], 'Missed constraint clauses')
        self.assertEqual(missed_regex, [], 'Missed regex clauses')

    return test_constraint_method

@GenerateTestMethods(test_name = 'ColumnConstraintsTest',
                     test_method=test_constraint_wrapper,
                     test_cases=[
                         #
                         # Charfield test cases - all attributes
                         #
                         {'case_name':'Default_Charfield', 'field_type':CharField},
                         {'case_name': 'Charfield_Unique', 'field_type': CharField,
                           'unique':True},
                         {'case_name': 'Charfield_NotNull',
                          'field_type': CharField,
                          'null': False, 'default':'Hello World'},
                         {'case_name': 'Charfield_Length',
                          'field_type': CharField,
                          'max_length': 382},
                         {'case_name': 'Charfield_Length_17',
                          'field_type': CharField,
                          'max_length': 17},
                         {'case_name': 'Charfield_Primary_key',
                          'field_type': CharField,
                          'primary': True},
                         {'case_name': 'Charfield_Unique_Primary_key',
                          'field_type': CharField,
                          'unique': True,
                          'primary': True},
                         {'case_name': 'Charfield_Unique_Not_Null_Primary_key',
                          'field_type': CharField, 'default':'Hello World',
                          'unique': True,
                          'null':False,
                          'primary': True},
                         {'case_name': 'Charfield_Unique_Not_Null_Primary_key_length',
                          'field_type': CharField, 'default':'Hello World',
                          'unique': True,
                          'null': False,
                          'primary': True,
                          'max_length':283},
                         #
                         # IntegerField test cases - all attributes
                         #
                         {'case_name': 'Default_IntegerField',
                          'field_type': IntegerField},
                         {'case_name': 'IntegerField_Unique',
                          'field_type': IntegerField,
                          'unique': True},
                         {'case_name': 'IntegerField_NotNull',
                          'field_type': IntegerField,
                          'null': False, 'default':1},
                         {'case_name': 'IntegerField_Primary_key',
                          'field_type': IntegerField,
                          'primary': True},
                         {'case_name': 'IntegerField_Unique_Primary_key',
                          'field_type': IntegerField,
                          'unique': True,
                          'primary': True},
                         {'case_name': 'IntegerField_Unique_Not_Null_Primary_key',
                          'field_type': IntegerField,'default':1,
                          'unique': True,
                          'null': False,
                          'primary': True},
                         #
                         # AutoField test cases - all attributes
                         #
                         {'case_name': 'AutoField_Default',
                             'field_type': AutoField, },
                         #
                         # DateField test cases - all attributes
                         #
                         {'case_name': 'Default_DateField',
                          'field_type': DateField},
                         {'case_name': 'DateField_Unique',
                          'field_type': DateField,
                          'unique': True},
                         {'case_name': 'DateField_NotNull',
                          'field_type': DateField, 'default':datetime.date(1,1,1),
                          'null': False},
                         {'case_name': 'DateField_Primary_key',
                          'field_type': DateField,
                          'primary': True},
                         {'case_name': 'DateField_Unique_Primary_key',
                          'field_type': DateField,
                          'unique': True,
                          'primary': True},
                         {
                             'case_name': 'DateField_Unique_Not_Null_Primary_key',
                             'field_type': DateField,'default':datetime.date(1,1,1),
                             'unique': True,
                             'null': False,
                             'primary': True},

                     ],
                     method_name_template='test_420_{index:03d}_{test_data[case_name]}',
                     method_doc_template='test {test_data[case_name]}'
                     )
class ColumnConstraintsTest(TestCaeExt):
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
