#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Test Suite for test_settings_manager.py

Summary : 
    <summary of module/class being tested>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
            
Test Series 
    100_* : Settings Manager
"""
import inspect
import sys
import unittest
from pathlib import Path

import click
from TempDirectoryContext import TempDirectoryContext as TDC

from core.settingsmanager import SettingsManager

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '01 Aug 2017'


class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_100_000_empty_setting(self):
        """Test the Settings manager with an empty settings files"""
        pre_path = sys.path

        with TDC() as tmp:
            full_path = Path(tmp) / 'settings.py'
            with open(str(full_path),'w') as fp:
                fp.write( "" )
            sm = SettingsManager(settings_file=full_path)
            with self.assertRaises(AttributeError):
                a = sm.db
        post_path = sys.path
        self.assertEqual(pre_path, post_path)


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
