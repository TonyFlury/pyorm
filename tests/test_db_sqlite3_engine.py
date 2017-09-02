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
    410_*** : test sqlite db engine
        410_000 ; Basic Engine operation - creation of databases etc
        410_1** : Tests the engine returns the right column name
        410_2** : Tests the engine creates the right SQL type for the column
        410_3** : Test the engine generate the right column check clauses
        410_4** : Testing the database adapters (duration & Decimal fields)
"""
import sys
import unittest
import click
import inspect
from pathlib import Path

import re
import datetime
import decimal

from TempDirectoryContext import TempDirectoryContext as TDC

from pyorm.db.engine.sqlite import Engine, Constants

import pyorm.db.models.fields as fields

from repeatedtestframework import GenerateTestMethods

import sqlite3

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

    def test_410_000_non_existant_db(self):
        """test that db is created if it doesn't exist"""
        with TDC() as temp_dir:
            file = Path(temp_dir) / 'database.db'
            self.assertFalse(file.exists(),'Database file exists pre test')
            eng = Engine(file)
            con = eng.connect()
            self.assertTrue(file.exists(), 'Database file does not exists post test')

#Todo Test existing databases and other items.

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
                                        'field_type':fields.CharField, 'field_name': 'test', 'db_column':None, 'expected': 'test'},
                         {'summary': 'db_column same as name',
                                      'field_type': fields.CharField, 'field_name': 'test',
                                          'db_column': 'test', 'expected': 'test'},
                         {'summary': 'db_column different to name',
                                      'field_type': fields.CharField, 'field_name': 'test',
                                          'db_column': 'test2', 'expected': 'test2'},

                         {'summary': 'db_column not provided',
                          'field_type': fields.AutoField, 'field_name': 'id',
                          'db_column': None, 'expected': 'id'},
                         {'summary': 'db_column provided',
                          'field_type': fields.AutoField, 'field_name': 'id',
                          'db_column': 'pkid', 'expected': 'pkid'},

                         {'summary': 'db_column not provided',
                          'field_type': fields.IntegerField, 'field_name': 'id',
                          'db_column': None, 'expected': 'id'},
                         {'summary': 'db_column provided',
                          'field_type': fields.IntegerField, 'field_name': 'id',
                          'db_column': 'pkid', 'expected': 'pkid'},

                         {'summary': 'db_column not provided',
                          'field_type': fields.DateField, 'field_name': 'id',
                          'db_column': None, 'expected': 'id'},
                         {'summary': 'db_column provided',
                          'field_type': fields.DateField, 'field_name': 'id',
                          'db_column': 'pkid', 'expected': 'pkid'},

                         {'summary': 'db_column not provided',
                          'field_type': fields.DateTimeField, 'field_name': 'id',
                          'db_column': None, 'expected': 'id'},
                         {'summary': 'db_column provided',
                          'field_type': fields.DateTimeField, 'field_name': 'id',
                          'db_column': 'pkid', 'expected': 'pkid'},

                         {'summary': 'db_column not provided',
                          'field_type': fields.EmailField, 'field_name': 'id',
                          'db_column': None, 'expected': 'id'},
                         {'summary': 'db_column provided',
                          'field_type': fields.EmailField, 'field_name': 'id',
                          'db_column': 'pkid', 'expected': 'pkid'},

                         {'summary': 'db_column not provided',
                          'field_type': fields.BooleanField, 'field_name': 'id',
                          'db_column': None, 'expected': 'id'},
                         {'summary': 'db_column provided',
                          'field_type': fields.BooleanField, 'field_name': 'id',
                          'db_column': 'pkid', 'expected': 'pkid'},

                     ],
                     method_name_template='test_410_1{index:02d}_{test_data[field_type].__name__}',
                     method_doc_template='test {test_data[field_type].__name__}: {test_data[summary]}'
                     )
# Test that Fields have the right DB column types
@GenerateTestMethods(test_name = 'Database_column_type_tests',
                     test_method=db_column_test_type_wrapper,
                     test_cases=[
                         {'field_type':fields.CharField, 'expected': 'text'},
                         {'field_type': fields.AutoField, 'expected': 'integer'},
                         {'field_type': fields.IntegerField, 'expected': 'integer'},
                         {'field_type': fields.EmailField, 'expected': 'text'},
                         {'field_type': fields.BooleanField, 'expected': 'boolean'},
                         {'field_type': fields.FloatField,'expected': 'float'},
                         {'field_type': fields.DateField,'expected':'date'},
                         {'field_type': fields.DateTimeField,'expected':'datetime'},
                         {'field_type': fields.DurationField,'expected':'duration'},
                         {'field_type': fields.DecimalField,'expected':'decimal'},
                         {'field_type':fields.BooleanField,'expected':'boolean'},
                         {'field_type': fields.BinaryField,'expected':'blob'}
                     ],

                     method_name_template='test_410_2{index:02d}_{test_data[field_type].__name__}',
                     method_doc_template='test {test_data[field_type].__name__}'
                     )
class DBColumnTypes(TestCaeExt):
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
                         {'case_name':'Default_Charfield', 'field_type':fields.CharField},
                         {'case_name': 'Charfield_Unique', 'field_type': fields.CharField,
                           'unique':True},
                         {'case_name': 'Charfield_NotNull',
                          'field_type': fields.CharField,
                          'null': False, 'default':'Hello World'},
                         {'case_name': 'Charfield_Length',
                          'field_type': fields.CharField,
                          'max_length': 382},
                         {'case_name': 'Charfield_Length_17',
                          'field_type': fields.CharField,
                          'max_length': 17},
                         {'case_name': 'Charfield_Primary_key',
                          'field_type': fields.CharField,
                          'primary': True},
                         {'case_name': 'Charfield_Unique_Primary_key',
                          'field_type': fields.CharField,
                          'unique': True,
                          'primary': True},
                         {'case_name': 'Charfield_Unique_Not_Null_Primary_key',
                          'field_type': fields.CharField, 'default': 'Hello World',
                          'unique': True,
                          'null':False,
                          'primary': True},
                         {'case_name': 'Charfield_Unique_Not_Null_Primary_key_length',
                          'field_type': fields.CharField, 'default': 'Hello World',
                          'unique': True,
                          'null': False,
                          'primary': True,
                          'max_length':283},
                         #
                         # IntegerField test cases - all attributes
                         #
                         {'case_name': 'Default_IntegerField',
                          'field_type': fields.IntegerField},
                         {'case_name': 'IntegerField_Unique',
                          'field_type': fields.IntegerField,
                          'unique': True},
                         {'case_name': 'IntegerField_NotNull',
                          'field_type': fields.IntegerField,
                          'null': False, 'default':1},
                         {'case_name': 'IntegerField_Primary_key',
                          'field_type': fields.IntegerField,
                          'primary': True},
                         {'case_name': 'IntegerField_Unique_Primary_key',
                          'field_type': fields.IntegerField,
                          'unique': True,
                          'primary': True},
                         {'case_name': 'IntegerField_Unique_Not_Null_Primary_key',
                          'field_type': fields.IntegerField, 'default':1,
                          'unique': True,
                          'null': False,
                          'primary': True},
                         #
                         # AutoField test cases - all attributes
                         #
                         {'case_name': 'AutoField_Default',
                             'field_type': fields.AutoField, },
                         #
                         # DateField test cases - all attributes
                         #
                         {'case_name': 'Default_DateField',
                          'field_type': fields.DateField},
                         {'case_name': 'DateField_Unique',
                          'field_type': fields.DateField,
                          'unique': True},
                         {'case_name': 'DateField_NotNull',
                          'field_type': fields.DateField, 'default':datetime.date(1, 1, 1),
                          'null': False},
                         {'case_name': 'DateField_Primary_key',
                          'field_type': fields.DateField,
                          'primary': True},
                         {'case_name': 'DateField_Unique_Primary_key',
                          'field_type': fields.DateField,
                          'unique': True,
                          'primary': True},
                         {
                             'case_name': 'DateField_Unique_Not_Null_Primary_key',
                             'field_type': fields.DateField, 'default':datetime.date(1, 1, 1),
                             'unique': True,
                             'null': False,
                             'primary': True},

                     ],
                     method_name_template='test_410_3{index:02d}_{test_data[case_name]}',
                     method_doc_template='test {test_data[case_name]}'
                     )
class ColumnConstraintsTest(TestCaeExt):
    def setUp(self):
        pass

#TODO test adapters
from pathlib import Path

class TestAdapters(TestCaeExt):
    def setUp(self):
        self.engine = Engine(':memory:')
        self.connection = self.engine.connect()

    def tearDown(self):
        self.connection.close()
        self.engine=None
        Engine.reset()

    def test_410_400_test_durationAdapater(self):

        cur = self.connection.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS TEST (d duration)')
        d = datetime.timedelta(days=23, hours=3, minutes=12, seconds=10, milliseconds=194, microseconds=496)

        cur.execute('INSERT INTO TEST(d) values(?)', (d,))

        cur.execute('SELECT d from TEST')
        row = cur.fetchone()
        self.assertEqual(d,row[0])

    def test_410_401_test_durationAdapater_None(self):

        cur = self.connection.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS TEST (d duration)')

        cur.execute('INSERT INTO TEST(d) values(NULL)')

        cur.execute('SELECT d from TEST')
        row = cur.fetchone()
        self.assertIsNone(row[0])

    def test_410_410_test_decimalAdapater(self):

        cur = self.connection.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS TEST (d decimal)')

        d = decimal.Decimal(19.73)
        cur.execute('INSERT INTO TEST(d) values(?)', (d,))

        cur.execute('SELECT d from TEST')
        row = cur.fetchone()
        self.assertAlmostEqual(d,row[0],places=10)

    def test_410_411_test_decimalAdapater_None(self):

        cur = self.connection.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS TEST (d duration)')

        cur.execute('INSERT INTO TEST(d) values(NULL)')

        cur.execute('SELECT d from TEST')
        row = cur.fetchone()
        self.assertIsNone(row[0])


class DateTrunc(unittest.TestCase):
    def setUp(self):
        self.engine = Engine(':memory:')
        self.connection = self.engine.connect()
        self.connection.execute('CREATE TABLE IF NOT EXISTS test (d date, ts timestamp)')
        self.connection.executemany('INSERT INTO test(d, ts) VALUES (?,?)',[
                                    (datetime.date(2012,11,19), datetime.datetime(2017,6,13, 13,34,9,320)),
                                    (datetime.date(2012,11,19), datetime.datetime(2017,6,13, 13,24,11)),
                                    (datetime.date(2011,12,15), datetime.datetime(2017,8,9, 9,5,0,11)),
                                    (datetime.date(2010,9,17),  datetime.datetime(2016,11,5, 22,55,59,230)),
                                    (datetime.date(2009,5,13), datetime.datetime(2015,11,5, 22,55,59)),
                                    (None,None)])

    def tearDown(self):
        self.connection.execute('DROP TABLE TEST;')
        self.connection.close()

    def test_410_500_TruncYear_Dates(self):
        cur = self.connection.execute('SELECT DISTINCT Truncyear(d) as d from TEST')
        years = [r['d'] for r in cur.fetchall()]
        self.assertEqual(len(years), 5)
        self.assertCountEqual(years,[('2012-1-1'),('2011-1-1'),('2010-1-1'),('2009-1-1'),(None)])

    def test_410_501_TruncYear_Datetimes(self):
        cur = self.connection.execute('SELECT DISTINCT Truncyear(ts) as ts from TEST')
        years = [r['ts'] for r in cur.fetchall()]
        self.assertEqual(len(years), 4)
        self.assertCountEqual(years,[('2017-1-1'),('2016-1-1'),('2015-1-1'),(None)])

    def test_410_510_TruncMonth_Dates(self):
        cur = self.connection.execute('SELECT DISTINCT Truncmonth(d) as d from TEST')
        years = [r['d'] for r in cur.fetchall()]
        self.assertEqual(len(years), 5)
        self.assertCountEqual(years,[('2012-11-1'),('2011-12-1'),('2010-09-1'),('2009-05-1'),(None)])

    def test_410_511_TruncMonth_Datetimes(self):
        cur = self.connection.execute('SELECT DISTINCT Truncmonth(ts) as ts from TEST')
        years = [r['ts'] for r in cur.fetchall()]
        self.assertEqual(len(years), 5)
        self.assertCountEqual(years,[('2017-06-1'),('2017-08-1'),('2016-11-1'),('2015-11-1'),(None)])

    def test_410_520_TruncDay_Dates(self):
        cur = self.connection.execute('SELECT DISTINCT Truncday(d) as d from TEST')
        years = [r['d'] for r in cur.fetchall()]
        self.assertEqual(len(years), 5)
        self.assertCountEqual(years,[('2012-11-19'),('2011-12-15'),('2010-09-17'),('2009-05-13'),(None)])

    def test_410_521_TruncDay_Datetimes(self):
        cur = self.connection.execute('SELECT DISTINCT Truncday(ts) as ts from TEST')
        years = [r['ts'] for r in cur.fetchall()]
        self.assertEqual(len(years), 5)
        self.assertCountEqual(years,[('2017-06-13'),('2017-08-09'),('2016-11-05'),('2015-11-05'),(None)])

    def test_410_531_TruncHour_Datetimes(self):
        cur = self.connection.execute('SELECT DISTINCT Trunchour(ts) as ts from TEST')
        years = [r['ts'] for r in cur.fetchall()]
        self.assertEqual(len(years), 5)
        self.assertCountEqual(years,[('2017-06-13 13:00:00'),('2017-08-09 09:00:00'),('2016-11-05 22:00:00'),('2015-11-05 22:00:00'),(None)])

    def test_410_541_Truncminutes_Datetimes(self):
        cur = self.connection.execute('SELECT DISTINCT Truncminutes(ts) as ts from TEST')
        years = [r['ts'] for r in cur.fetchall()]
        self.assertEqual(len(years), 6)
        self.assertCountEqual(years,[('2017-06-13 13:34:00'),('2017-06-13 13:24:00'),('2017-08-09 09:05:00'),('2016-11-05 22:55:00'),('2015-11-05 22:55:00'),(None)])

    def test_410_541_Truncseconds_Datetimes(self):
        cur = self.connection.execute('SELECT DISTINCT Truncseconds(ts) as ts from TEST')
        years = [r['ts'] for r in cur.fetchall()]
        self.assertEqual(len(years), 6)
        self.assertCountEqual(years,[('2017-06-13 13:34:09'),('2017-06-13 13:24:11'),('2017-08-09 09:05:00'),('2016-11-05 22:55:59'),('2015-11-05 22:55:59'),(None)])

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
