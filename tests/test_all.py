#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of test_all.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
    
Test Series : 
    0xx - cli help
    100 - validators & other core functionality
    200 - Fields & Models - basic stuff only
        20* - Fields - validation and default values
        25* - Models - creation & setting of attributes
        28* - Managers - creation of default and other managers
    300 - Data base connectivity
    400 - db Engines
        410 - SQLITE
    500 - Query Sets
    600 - Compiler
    700 - Managers
    800 - Migrations
    900 - Pyorm Console & testing capabilities
"""

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '30 Jul 2017'

import click
import unittest
import importlib
from pathlib import Path
from os import listdir
import inspect


class OrderedTestSuite(unittest.TestSuite):
    def __iter__(self):
        return iter(sorted(self._tests, key=lambda x:str(x)))

def load_tests(loader, load_module):

    classes = [cls for name, cls in inspect.getmembers(load_module,
                                                 inspect.isclass)
                                    if issubclass(cls, unittest.TestCase)]

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
    suite = OrderedTestSuite()

    this_dir = Path(__file__).parent

    module_names = [py[:-3] for py in listdir(str(this_dir)) if py.endswith('.py') and py.startswith('test') and py not in ['__init__.py', str(Path(__file__).name)]]

    for module_name in module_names:
        the_module = importlib.import_module(module_name)
        suite.addTests(load_tests(loader=ldr, load_module=the_module))

    unittest.TextTestRunner(verbosity=verbose).run(suite)


if __name__ == '__main__':
    main()
else:
    import sys
    print('Run test_all direct from the command line - do not run as if it is a unittest moudle')
    sys.exit(1)