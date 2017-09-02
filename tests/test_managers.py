#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Test Suite for test_managers

Summary : 
    <summary of module/class being tested>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....

Test Series
    280 - Test manager are created by default
"""
import sys
import inspect
import unittest
import click

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '26 Aug 2017'

from pyorm.db.models.models import Model
from pyorm.db.models.managers import Manager
from pyorm.db.models.fields import CharField

class DefaultManagerCreation(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_280_000_manager_creation(self):
        """Test that objects manager is created if no manager exists"""
        class TestClass(Model):
            name = CharField()

        inst = TestClass()

        self.assertTrue(hasattr(inst, 'objects'), msg='Objects attributes not created')
        self.assertIsInstance(inst.objects, Manager, msg='Objects exists but is not a manager')
        self.assertEqual(inst.objects.model, TestClass)


    def test_200_001_manager_exists(self):
        class TestClass(Model):
            tests = Manager()
            name = CharField()

        inst = TestClass()

        self.assertFalse(hasattr(inst,'objects'), msg='Objects attribute created in error')
        self.assertIsInstance(inst.tests,Manager,msg='tests Attribute isn\'t a Manager')


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
