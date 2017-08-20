#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Test Suite for test_models.py

Summary : 
    <summary of module/class being tested>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
import sys
import inspect
import unittest
import click

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '19 Aug 2017'

from pyorm.db.models.models import Model
from pyorm.db.models.fields import CharField
from pyorm.core.validators import RegexValidator

class TestBasicModelFunctionality(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_000_creation_of_instance(self):
        class TestModel(Model):
            name = CharField()

        a = TestModel()
        self.assertTrue(hasattr(a,'name'))

    def test_000_001_field_validation(self):
        class TestModel(Model):
            name = CharField(validator=RegexValidator(regex=r'Hello'))

        with self.assertRaisesRegex(AttributeError,'Error setting \'name\' field: Invalid value'):
            a = TestModel(name='Goodbye')

    def test_000_002_field_setting(self):
        class TestModel(Model):
            name = CharField(validator=RegexValidator(regex=r'Hello',message='Ooops - that isn\'t right'))

        a = TestModel()

        with self.assertRaisesRegex(AttributeError,'Error setting \'name\' field: Opps - that isn\'t right'):
            a.name = 'Goodbye'

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
