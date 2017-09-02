#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Test Suite for test_model_to_engine.py

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

from importlib.machinery import ModuleSpec
import importlib.util

from pyorm.core.settingsmanager import SettingsManager
from pyorm.core.validators import RegexValidator
import pyorm.core.exceptions as exceptions

from unittest.mock import MagicMock, call

from datetime import date

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '23 Aug 2017'

from pathlib import Path

class EngineImporterAndInitialisation(unittest.TestCase):

    @staticmethod
    def dummy_module(name, source):
        dummy_module = importlib.util.module_from_spec(
            ModuleSpec(name=name, loader=None))
        exec(source, dummy_module.__dict__)
        sys.modules[name] = dummy_module
        return dummy_module

    def setUp(self):

        self.Engine_module = self.dummy_module('dummy_engine_module',
"""
from unittest.mock import MagicMock
from pyorm.db.engine._core import EngineCore

inst = MagicMock(spec=EngineCore, name='Engine instance')
Engine = MagicMock(spec_set=EngineCore,return_value=inst,name='Engine class')
""")
        self.Engine = self.Engine_module.Engine
        self.Engine.reset_mock()
        if 'pyorm.db.models.models' in sys.modules:
            del sys.modules['pyorm.db.models.models']

    def tearDown(self):
        pass

    def test_400_001_ImportEngine(self):
        """Show that the ImportEngine class can import an engine module, given its name"""
        from pyorm.db.engine.common import ImportEngine
        with SettingsManager(settings_file=Path('./settings.py'),
                             overrides={
                                 'engine': 'dummy_engine_module.Engine'},
                             dummy_module=True) as sm:
            ie = ImportEngine(sm)
            engine = ie.engine_cls()
            inst = ie.engine_inst()
            self.assertIs(engine, self.Engine)
            self.assertIs(inst, self.Engine_module.inst)

# ToDo test error conditions

    def test_400_001_ImportEngineTwice(self):
        """Try to Two instances of the Import Engine class """
        from pyorm.db.engine.common import ImportEngine
        with SettingsManager(settings_file=Path('./settings.py'),
                             overrides={
                                 'engine': 'dummy_engine_module.Engine'},
                             dummy_module=True) as sm:
            ie = ImportEngine(sm)
            ie2 = ImportEngine(sm)
            self.assertIs(ie,ie2)

    def test_400_002_sm_initialisation(self):
        """Test that importing the Model directory will start the engine"""
        with SettingsManager(Path('./settings.py'),overrides={'engine':'dummy_engine_module.Engine'},dummy_module=True) as sm:

            from pyorm.db.engine.common import ImportEngine
            from pyorm.db.models.models import Model

            ie = ImportEngine(sm)
            engine_inst = ie.engine_inst()
            engine_inst.start.aseert_called_once()

    #Todo - test errors from SettingsManager - need to inject mock into replace SettingsManager

class TestGet(unittest.TestCase):
    """Test the get method against a mocked engine class - test interactions between model and engine"""
    @staticmethod
    def dummy_module(name, source):
        dummy_module = importlib.util.module_from_spec(
            ModuleSpec(name=name, loader=None))
        exec(source, dummy_module.__dict__)
        sys.modules[name] = dummy_module
        return dummy_module

    def setUp(self):
        self.Engine_module = self.dummy_module(
            'dummy_engine_module',
            """
from unittest.mock import MagicMock
from pyorm.db.engine._core import EngineCore

inst = MagicMock(spec=EngineCore, name='Engine instance')
Engine = MagicMock(spec_set=EngineCore,return_value=inst,name='Engine class')
""")
        self.Engine = self.Engine_module.Engine
        self.Engine.reset_mock()
        self.Engine_inst = self.Engine_module.inst

        if 'pyorm.db.models.models' in sys.modules:
            del sys.modules['pyorm.db.models.models']

    def tearDown(self):
        pass

    def test_410_001_SimpleGet(self):
        """Execute a simple get - test that engine.get is called correctly"""
        with SettingsManager(Path('./settings.py'), overrides={
            'engine': 'dummy_engine_module.Engine'}, dummy_module=True) as sm:

            from pyorm.db.models.models import Model
            import pyorm.db.models.fields as fields

            engine_inst = self.Engine_inst

            engine_inst.get.return_value = {'id':17,'name':'Tony','date':date(year=2014,month=8,day=26)}

            class TestClass(Model):
                name = fields.CharField(default='Tony')
                date = fields.DateField()

            model_inst = TestClass.get(id=17)

            engine_inst.get.assert_called_once_with(model=TestClass, id=17)

            self.assertEqual(model_inst.id, 17)
            self.assertEqual(model_inst.name, 'Tony')
            self.assertEqual(model_inst.date, date(year=2014, month=8, day=26))

    def test_410_002_SimpleGetWithColumnNames(self):
        """Test Model.get with column names"""
        with SettingsManager(Path('./settings.py'),
                            overrides={'engine': 'dummy_engine_module.Engine'},
                            dummy_module=True) as sm:

            from pyorm.db.models.models import Model
            import pyorm.db.models.fields as fields

            engine_inst = self.Engine_inst

            engine_inst.get.return_value = {'id':17,'persons_name':'Tony','date':date(year=2014,month=8,day=26)}

            class TestClass(Model):
                name = fields.CharField(default='Tony', db_column='persons_name')
                date = fields.DateField()

            model_inst = TestClass.get(id=17)

            engine_inst.get.assert_called_once_with(model=TestClass, id=17)

            self.assertEqual(model_inst.id, 17)
            self.assertEqual(model_inst.name, 'Tony')
            self.assertEqual(model_inst.date, date(year=2014, month=8, day=26))

    def test_410_003_SimpleGetInvalidData(self):
        """Test Model.get with invalid data returned - violating basic field attributes"""
        with SettingsManager(Path('./settings.py'),
                            overrides={'engine': 'dummy_engine_module.Engine'},
                            dummy_module=True) as sm:

            from pyorm.db.models.models import Model
            import pyorm.db.models.fields as fields

            engine_inst = self.Engine_inst

            engine_inst.get.return_value = {'id':17,'name':None,'date':date(year=2014,month=8,day=26)}

            class TestClass(Model):
                name = fields.CharField(default='Tony', null=False)
                date = fields.DateField()

            with self.assertRaisesRegex(AttributeError,expected_regex='Invalid value for field \'name\': value is None, but \'null\' attribute is False'):
                model_inst = TestClass.get(id=17)

    def test_410_004_SimpleGetInvalidData(self):
        """Test Model.get with invalid data returned - violating custom validator"""
        with SettingsManager(Path('./settings.py'),
                            overrides={'engine': 'dummy_engine_module.Engine'},
                            dummy_module=True) as sm:

            from pyorm.db.models.models import Model
            import pyorm.db.models.fields as fields

            engine_inst = self.Engine_inst

            engine_inst.get.return_value = {'id':17,'name':'tony','date':date(year=2014,month=8,day=26)}

            class TestClass(Model):
                name = fields.CharField(default='Tony', validator=RegexValidator(regex=r'[A-Z].*',message='Must start with a lower case letter'))
                date = fields.DateField()

            with self.assertRaisesRegex(AttributeError,expected_regex='Invalid value for field \'name\': Must start with a lower case letter'):
                model_inst = TestClass.get(id=17)

    def test_410_005_SimpleGetInvalidDataExtraColumns(self):
        """Test Model.get with invalid data returned - unknown columns"""
        with SettingsManager(Path('./settings.py'),
                            overrides={'engine': 'dummy_engine_module.Engine'},
                            dummy_module=True) as sm:

            from pyorm.db.models.models import Model
            import pyorm.db.models.fields as fields

            engine_inst = self.Engine_inst

            engine_inst.get.return_value = {'id':17,'name':'tony','date':date(year=2014,month=8,day=26),'version':'1.0'}

            class TestClass(Model):
                name = fields.CharField(default='Tony', validator=RegexValidator(regex=r'[A-Z].*',message='Must start with a lower case letter'))
                date = fields.DateField()

            with self.assertRaisesRegex(exceptions.ColumnError, expected_regex='Unexpected column from database: column \'version\' is not known on the \'TestClass\' model'):
                model_inst = TestClass.get(id=17)

    def test_410_006_SimpleGetNoDataException(self):
        """Test Model.get with invalid data returned - DoesNotExist exception"""
        with SettingsManager(Path('./settings.py'),
                            overrides={'engine': 'dummy_engine_module.Engine'},
                            dummy_module=True) as sm:

            from pyorm.db.models.models import Model
            import pyorm.db.models.fields as fields

            engine_inst = self.Engine_inst

            engine_inst.get.side_effect=exceptions.DoesNotExist()

            class TestClass(Model):
                name = fields.CharField()
                date = fields.DateField()

            with self.assertRaises(exceptions.DoesNotExist):
                model_inst = TestClass.get(id=17)

    def test_410_007_SimpleGetTooManyRows(self):
        """Test Model.get with invalid data returned - MultipleObjects exception"""
        with SettingsManager(Path('./settings.py'),
                            overrides={'engine': 'dummy_engine_module.Engine'},
                            dummy_module=True) as sm:

            from pyorm.db.models.models import Model
            import pyorm.db.models.fields as fields

            engine_inst = self.Engine_inst

            engine_inst.get.side_effect=exceptions.MultipleObjects()

            class TestClass(Model):
                name = fields.CharField()
                date = fields.DateField()

            with self.assertRaises(exceptions.MultipleObjects):
                model_inst = TestClass.get(id=17)

    def test_410_008_SimpleGetTooManyArguments(self):
        """Test Model.get with invalid arguments - more than one argument/value pair"""
        with SettingsManager(Path('./settings.py'),
                            overrides={'engine': 'dummy_engine_module.Engine'},
                            dummy_module=True) as sm:

            from pyorm.db.models.models import Model
            import pyorm.db.models.fields as fields

            engine_inst = self.Engine_inst

            engine_inst.get.side_effect=exceptions.MultipleObjects()

            class TestClass(Model):
                name = fields.CharField()
                date = fields.DateField()

            with self.assertRaisesRegex(AttributeError,'Incorrect arguments to \'get\': need only one field/value argument pair'):
                model_inst = TestClass.get(id=17,name='Tony')

    def test_410_009_SimpleGetUnknownField(self):
        """Test Model.get with invalid arguments - more than one argument/value pair"""
        with SettingsManager(Path('./settings.py'),
                            overrides={'engine': 'dummy_engine_module.Engine'},
                            dummy_module=True) as sm:

            from pyorm.db.models.models import Model
            import pyorm.db.models.fields as fields

            engine_inst = self.Engine_inst

            engine_inst.get.return_value={}

            class TestClass(Model):
                name = fields.CharField()
                date = fields.DateField()

            with self.assertRaisesRegex(AttributeError,'Unknown field name: \'version\' is not a field on \'TestClass\' model'):
                model_inst = TestClass.get(version='1.0')

# Todo Test Objects query set/Manager


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


class EngineLoader(unittest.TestCase):
    @staticmethod
    def dummy_module(name, source):
        dummy_module = importlib.util.module_from_spec(
            ModuleSpec(name=name, loader=None))
        exec(source, dummy_module.__dict__)
        sys.modules[name] = dummy_module
        return dummy_module

    def setUp(self):
        self.Engine_module = self.dummy_module('dummy_engine_module',
                                               """
from unittest.mock import MagicMock
from pyorm.db.engine._core import EngineCore

Engine = MagicMock(spec_set=EngineCore,return_value=MagicMock())""")

        self.Engine = self.Engine_module.Engine
        self.Engine.reset_mock()
        if 'pyorm.db.models.models' in sys.modules:
            del sys.modules['pyorm.db.models.models']

    def tearDown(self):
        pass

