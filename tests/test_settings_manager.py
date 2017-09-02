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
    15*_* : Settings Manager
"""
import inspect
import sys
import unittest
from pathlib import Path

import click
from TempDirectoryContext import TempDirectoryContext as TDC

from pyorm.core.settingsmanager import SettingsManager

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '01 Aug 2017'


class TestBasicSettingsManager(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_150_000_empty_setting(self):
        """Test the Settings manager with an empty settings files"""
        pre_path = sys.path

        self.assertNotIn('settings', sys.modules)

        with TDC() as tmp:
            full_path = Path(tmp) / 'settings.py'
            with open(str(full_path),'w') as fp:
                fp.write( "" )
            sm = SettingsManager(settings_file=full_path)
            self.assertIsNone(sm.get('db'))

            # Check that a settings module actually exists
            self.assertIn('settings', sys.modules)

            # Check that we can try to get attributes directly from the module
            with self.assertRaises(AttributeError):
                settings = sys.modules['settings']
                a = settings.db

            # Close the settings manager
            sm.close()

            # Prove that the setting manager is no longer usable
            with self.assertRaises(AttributeError):
                sm.get('db')

            # Confirm that the settings module has been removed
            self.assertNotIn('settings', sys.modules)

        post_path = sys.path
        self.assertEqual(pre_path, post_path)

    def test_150_001_single_setting(self):

        with TDC() as tmp:
            full_path = Path(tmp) / 'settings.py'
            with open(str(full_path),'w') as fp:
                fp.write(
                    """engine='pyorm.db.engine.sqlite'""" )

            sm = SettingsManager(settings_file=full_path)
            self.assertEqual(sm.get('engine'), 'pyorm.db.engine.sqlite')
            sm.close()

    def test_150_002_single_setting_overide(self):
        with TDC() as tmp:
            full_path = Path(tmp) / 'settings.py'
            with open(str(full_path), 'w') as fp:
                fp.write(
                    """engine='pyorm.db.engine.sqlite'""")
            sm = SettingsManager(settings_file=full_path,
                                        overrides={'db':'database.db','engine':'193.17'})
            self.assertEqual(sm.get('engine'), '193.17')
            self.assertEqual(sm.get('db'),'database.db')
            sm.close()

    def test_150_003_missing_settings(self):
        with TDC() as tmp:
            full_path = Path(tmp) / 'settings.py'
            with self.assertRaises(ImportError):
                sm = SettingsManager(settings_file=full_path )

    def test_150_004_missing_settings_dummy_module(self):
        with TDC() as tmp:
            full_path = Path(tmp) / 'settings.py'
            sm = SettingsManager(settings_file=full_path, dummy_module=True )

            # Check that a settings module actually exists
            self.assertIn('settings', sys.modules)

            # Dummy Module should be empty
            with self.assertRaises(AttributeError):
                db = sys.modules['settings'].db

            self.assertEqual(sm.get('db'), None)

            sm.close()

    def test_150_005_missing_settings_dummy_module_overrides(self):
        with TDC() as tmp:
            full_path = Path(tmp) / 'settings.py'
            sm = SettingsManager(settings_file=full_path,
                                 overrides={'db':'database.db'},
                                 dummy_module=True )
            # Check that a settings module actually exists
            self.assertIn('settings', sys.modules)

            # Dummy Module should be empty
            with self.assertRaises(AttributeError):
                db = sys.modules['settings'].db

            self.assertEqual(sm.get('db'), 'database.db')
            sm.close()

class SettingsManagerContext(unittest.TestCase):
    def setUp(self):
        self.tdc = TDC()
        self.tmp_dir = self.tdc.__enter__()

    def make_settings_file(self, path:Path, settings:dict):
        with open(str(path),'w') as fp:
            for k,v in settings.items():
                fp.write('{} = {!r}'.format(k,v))

    def tearDown(self):
        self.tdc.__exit__( None, None, None)
        del self.tmp_dir
        del self.tdc

    def test_155_001_settings_manager_context_manager(self):
        self.make_settings_file(path=Path(self.tmp_dir) / 'settings.py',
                                settings={'engine':'pyorm.db.engine.sqlite'})
        with SettingsManager(settings_file=Path(self.tmp_dir) / 'settings.py') as sm:
            self.assertIn('settings', sys.modules)
            self.assertEqual(sm.get('engine'), 'pyorm.db.engine.sqlite')

        self.assertNotIn('settings', sys.modules)

    def test_155_002_settings_manager_context_manager(self):
        self.make_settings_file(path=Path(self.tmp_dir) / 'settings.py',
                                settings={'engine':'pyorm.db.engine.sqlite'})
        with SettingsManager(settings_file=Path(self.tmp_dir) / 'settings.py',
                                                overrides={'db':'database.db'}) as sm:
            self.assertIn('settings', sys.modules)
            self.assertEqual(sm.get('engine'), 'pyorm.db.engine.sqlite')
            self.assertEqual(sm.get('db'),'database.db')

        self.assertNotIn('settings', sys.modules)


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
