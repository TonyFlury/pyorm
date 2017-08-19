#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of test_initialise

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a developer I want to initialise an application so that my application 
    can I remove sources of systemic errors.

Testable Statements :
    Does the initialise command report errors correctly
    Does the initialise command create the correct directories
    Does the initialise command create the sample model.py
    Does the initialise command create the sample settings.py
    Does the initialise command operate as expected in dry-run mode
            (report on file/directory creation but not actually execute them)
            
    Note:
        There is no need to test the --help option - that is tested in the
        test_cli-help.py
        
    Test Series: 
        test_010_* : Test initialise command  
    
"""

import unittest

# Modules needed for auto ordering of test classes
import sys
import inspect

#Modules needed for click interface
import click

# Modules needed to test click interface
from click.testing import CliRunner
from pyorm._cli import _main

#Modules needed to execute the actual tests
import os
import stat


__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '23 Jul 2017'


class InitialiseErrors(unittest.TestCase):
    """Test for Errors resulting from invoking the initialise command"""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_010_000_InvalidOptions(self):
        """Test for an invalid option"""
        runner = CliRunner()
        result = runner.invoke(_main.main, ['initialise', '-d'])
        self.assertEqual(result.exit_code, click.UsageError.exit_code)
        self.assertIn('Error: no such option: -d', result.output)

    def test_010_001_InvalidPathNotExist(self):
        """Test for a path that doesn't exist"""
        dir_name = 'Does_not_exist'
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(_main.main, ['initialise', dir_name])
            self.assertEqual(result.exit_code, click.UsageError.exit_code)
            self.assertIn('Directory \"{}\" does not exist'.format(dir_name), result.output)

    def test_010_003_InvalidPathNoRead(self):
        """Test for a path that is not readable"""
        dir_name = 'CannotRead'
        unreadable_stat = stat.S_IWRITE | stat.S_IEXEC
        runner = CliRunner()
        with runner.isolated_filesystem():
            os.mkdir(dir_name)
            os.chmod(dir_name, unreadable_stat)

            result = runner.invoke(_main.main, ['initialise',dir_name])
            self.assertEqual(result.exit_code, click.UsageError.exit_code)
            self.assertIn('Directory \"{}\" is not readable'.format(dir_name), result.output)

            os.chmod(dir_name, unreadable_stat | stat.S_IREAD)
            os.rmdir(dir_name)

    def test_010_004_InvalidPathNotWrite(self):
        """Test for a path that is not writable"""
        dir_name = 'CannotWrite'
        unwriteable_stat = stat.S_IREAD | stat.S_IEXEC

        runner = CliRunner()
        with runner.isolated_filesystem():
            os.mkdir(dir_name)
            os.chmod(dir_name, unwriteable_stat)
            result = runner.invoke(_main.main, ['initialise', dir_name])
            self.assertEqual(result.exit_code, click.UsageError.exit_code)
            self.assertIn('Directory \"{}\" is not writable'.format(dir_name), result.output)
            os.chmod(dir_name, stat.S_IWRITE | unwriteable_stat)
            os.rmdir(dir_name)

    def test_010_005_InvalidPathNotDirectory(self):
        """Test for a path that is not a directory"""
        filename = 'This_is_no_a_directory'

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open(filename,'w') as fp:
                result = runner.invoke(_main.main, ['initialise', filename])
                self.assertEqual(result.exit_code, click.UsageError.exit_code)
                self.assertIn('Directory \"{}\" is a file'.format(filename), result.output)

            os.remove(filename)

class InitialiseDryRun(unittest.TestCase):
    """Test for initialise command dry-run mode"""
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def dir_contents(self, expected_result=True):
        """Return a boolean list of test results - no specificity"""

        # List of tuples - name, test, finish_fast
        expected = [ ('.', lambda p: os.listdir(p).sort() == ['migrations','models','settings.py']),
                     ('migrations', os.path.isdir,),
                     ('models',os.path.isdir,),
                     ('settings.py', os.path.isfile,),
                     ('models', lambda p: p in os.listdir('.') and os.listdir(p) == ['models.py']),
                     ('models/model.py', lambda p: 'models' in os.listdir('.') and os.path.isfile),
                     ('migrations', lambda p : 'migrations' in os.listdir('.') and os.listdir(p) == [] ), ]


        return [True for p, t in expected if t(p)]

    def test_010_000_DryRun(self):
        """Test for dry-run mode - output but no directory changes"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(_main.main, ['initialise', '--dry_run'])
            self.assertFalse(any(self.dir_contents()),msg='Unexpected directory contents')
            self.assertEqual(result.exit_code,0)
            self.assertIn('\"models\" directory', result.output, msg='No metion of models directory')
            self.assertIn('\"migrations\" directory', result.output, msg='No metion of migrations directory')
            self.assertIn('\"models\models.py\"', result.output, msg='No metion of models\\models.py directory')
            self.assertIn('\"settings.py\"', result.output, msg='No metion of settings.py directory')

    def test_010_001_Active(self):
        """Test for normal mode - look for directory changes"""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(_main.main, ['initialise', '.'])
            self.assertTrue(all(self.dir_contents()),msg='Unexpected directory contents')
            self.assertEqual(result.exit_code,0)
            self.assertIn('\"models\" directory', result.output, msg='No metion of models directory')
            self.assertIn('\"migrations\" directory', result.output, msg='No metion of migrations directory')
            self.assertIn('\"models\models.py\"', result.output, msg='No metion of models\\models.py directory')
            self.assertIn('\"settings.py\"', result.output, msg='No metion of settings.py directory')

def load_tests(loader, tests=None, pattern=None):

    # Generate a list of classes in the order in which they are included in the
    # source code.
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
@click.option('-v','--verbose', default=2, help='Level of output', count=True)
@click.option('-s','--silent', is_flag=True, default=False)
def main( verbose, silent):

    verbose = 0 if silent else verbose

    ldr = unittest.TestLoader()
    test_suite = load_tests(ldr)
    unittest.TextTestRunner(verbosity=verbose).run(test_suite)

if __name__ == '__main__':
    main()