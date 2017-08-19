#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Test Suite for test_settings

Summary : 
    Test cli help pages
Use Case : 
    As a user of pyorm I want the cli help pages to contain key facts So that I can get the facts I need

Test Series: 
    test_000_* : Test cli help pages for all commands and sub commands.

"""

import unittest
import click
from click.testing import CliRunner
import inspect
import sys

from pyorm._cli import _main

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '23 Jul 2017'


class MainHelp(unittest.TestCase):
    """Tests for contents of Main Help Page - pyorm --help
    
       test series 000_0**
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_000_basic_summary(self):
        """Confirm summary appears on basic help page"""
        runner = CliRunner()
        result = runner.invoke(_main.main,['--help'])
        self.assertEqual(result.exit_code,0)
        self.assertIn('pyorm Management command', result.output, msg='Help title not found')
        self.assertIn('Creation, migration and reporting on application database', result.output, msg='Help summary')

    def test_000_001_help_help(self):
        """Confirm help page includes help instructions"""
        runner = CliRunner()
        result = runner.invoke(_main.main,['--help'])
        self.assertEqual(result.exit_code,0)
        self.assertIn('--help', result.output, msg='Help on --help option not found')

    def test_000_002_verbosity_help(self):
        """Confirm help page includes verbose option instructions"""
        runner = CliRunner()
        result = runner.invoke(_main.main,['--help'])
        self.assertEqual(result.exit_code,0)
        self.assertIn('-v, --verbose', result.output, msg='Help on -v/--verbose option not found')

    def test_000_003_version_help(self):
        """Confirm help page includes version option instructions"""
        runner = CliRunner()
        result = runner.invoke(_main.main,['--help'])
        self.assertEqual(result.exit_code,0)
        self.assertIn('--version', result.output, msg='Help on --version option not found')

    def test_000_004_commands_help(self):
        """Confirm help page includes List of commands"""
        runner = CliRunner()
        result = runner.invoke(_main.main, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Commands', result.output,msg='Commands subsection not found')

        pos = result.output.find('Commands')

        self.assertIn('data', result.output[pos:], msg='Help on data command not found')
        self.assertIn('initialise', result.output[pos:], msg='Help on initialise command not found')
        self.assertIn('migration', result.output[pos:], msg='Help on migration command not found')
        self.assertIn('show', result.output[pos:], msg='Help on show command not found')

class InitialiseHelp(unittest.TestCase):
    """Tests for contents of Initialise Help Page - pyorm initialise --help
    
           test series 000_1**
           
           100 Basic Help
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_100_initialise_help(self):
        """Confirm help for initialise sub-command contains a summary"""
        runner = CliRunner()
        result = runner.invoke(_main.main, ['initialise','--help'])
        self.assertEqual(result.exit_code,0)
        self.assertIn('Usage: pyorm initialise [OPTIONS] PATH', result.output)
        self.assertIn('Initialise the application database', result.output)
        self.assertIn('--help', result.output)

    def test_000_105_initialise_abbreviation_help(self):
        """confirm initialise available via an abbreviation"""
        runner = CliRunner()
        result = runner.invoke(_main.main, ['init','--help'])
        self.assertEqual(result.exit_code,0)
        self.assertIn('Initialise the application database', result.output)

class MigrationHelp(unittest.TestCase):
    """Tests for contents of migration Help Pages - pyorm nigration -help & sub commands
    
       test Series 000_2**
       
       200 - Basic Help
       210 - Migration create Help
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_000_200_migrate_help(self):
        """Confirm summary of migrate sub-command"""
        runner = CliRunner()
        result = runner.invoke(_main.main, ['migration','--help'])
        self.assertEqual(result.exit_code,0)
        self.assertIn('Sub-commands to create, verify and apply migration scripts', result.output,
                      msg = 'Command Summary not found')

    def test_000_201_migrate_commands_help(self):
        """Confirm migration sub-commands are documented"""
        runner = CliRunner()
        result = runner.invoke(_main.main, ['migration','--help'])
        self.assertEqual(result.exit_code,0)

        cmd_pos = result.output.find('Commands')
        opt_pos = cmd_pos + result.output.find('Options')

        self.assertIn('create', result.output[cmd_pos:opt_pos], msg = 'Command create summary not found')
        self.assertIn('apply', result.output[cmd_pos:opt_pos], msg = 'Command apply summary not found')
        self.assertIn('sql', result.output[cmd_pos:opt_pos], msg = 'Command sql summary not found')
        self.assertIn('rollback', result.output[cmd_pos:opt_pos], msg = 'Command rollback summary not found')
        self.assertIn('show', result.output[cmd_pos:opt_pos], msg = 'Command show summary not found')

    def test_000_205_Migration_Abbreviation(self):
        """Test that migration command can be abbreviated"""
        runner = CliRunner()
        result = runner.invoke(_main.main, ['mig','--help'])
        self.assertEqual(result.exit_code,0)

    def test_000_210_migrate_create_help(self):
        """Confirm migration create command summary is documented"""
        runner = CliRunner()
        result = runner.invoke(_main.main, ['migration','create','--help'])
        self.assertEqual(result.exit_code,0)
        self.assertIn('Create migration scripts based on models or changes to models',
                      result.output, msg='Command Summary not found')

    def test_000_215_migrate_create_arguments_options_help(self):
        """Confirm migration create command summary is documented"""
        runner = CliRunner()
        result = runner.invoke(_main.main, ['migration', 'create','--help'])

        self.assertIn('Arguments:', result.output, msg='Arguments section not found')
        arg_pos = result.output.find('Arguments')

        self.assertIn('Options:', result.output[arg_pos:], msg='Options section not found')
        opt_pos = arg_pos + result.output[arg_pos:].find('Options')

        self.assertIn('PATH', result.output[arg_pos:opt_pos],msg='PATH argument documentation not found')

        self.assertIn('-n, --dry_run', result.output[opt_pos:],msg='-n/--dry_run option documentation not found')
        self.assertIn('--help', result.output[opt_pos:],msg='--help option documentation not found')


def load_tests(loader, tests=None, pattern=None):
    classes = [cls for name, cls in inspect.getmembers(sys.modules[__name__],
                                                 inspect.isclass)
                                    if issubclass(cls, unittest.TestCase)]

    classes.sort(key=lambda cls_:cls_.setUp.__code__.co_firstlineno)

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