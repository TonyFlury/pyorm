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

Test Series
    25n_* : test the database models basic functionality
        250 - Model class and Model class attribute
        251 - Model creation
        252 - Model creation with default values
        253 - Model creation with arguments
        254 - Model creation with errors
        255 - Model setting with errors
"""
import inspect
import sys
import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal

import click
from repeatedtestframework import GenerateTestMethods

import pyorm.db.models.fields as fields
from pyorm.core.validators import RegexValidator
from pyorm.db.models.models import Model
import pyorm.core.exceptions as exceptions

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '19 Aug 2017'



class ModelClassAttributes(unittest.TestCase):
    def setUp(self):
        pass

    def test_250_001_model_class_table_name(self):
        """Check that the table name is recorded correctly"""
        class TestModel(Model):
            artist_name = fields.CharField()
            birth_date = fields.DateField(db_column='birth')
            death_date = fields.DateField(db_column='death')

        self.assertEqual(TestModel.table_name(), 'TestModel')

    def test_250_002_model_class_table_name(self):
        """Check that the table name is recorded correctly when overriden"""
        class TestModel(Model):
            _table = 'SingerSongwriter'
            artist_name = fields.CharField()
            birth_date = fields.DateField(db_column='birth')
            death_date = fields.DateField(db_column='death')

        self.assertEqual(TestModel.table_name(), 'SingerSongwriter')

    def test_250_010_model_class_db_field_by_name(self):
        """Test db_field_by_name class method finds valid fields"""
        class TestModel(Model):
            artist_name = fields.CharField()
            birth_date = fields.DateField()
            death_date = fields.DateField()

        self.assertEqual(TestModel.db_field_by_name('artist_name'), TestModel.artist_name)
        self.assertEqual(TestModel.db_field_by_name('birth_date'), TestModel.birth_date)
        self.assertEqual(TestModel.db_field_by_name('death_date'), TestModel.death_date)

    def test_250_015_model_class_db_field_by_name(self):
        """Test db_field_by_name class method doesn't find invalid fields"""
        class TestModel(Model):
            artist_name = fields.CharField()
            birth_date = fields.DateField(db_column='birth')
            death_date = fields.DateField(db_column='death')

        self.assertIsNone(TestModel.db_field_by_name('publish_date'))

    def test_250_020_model_class_db_column_to_attr(self):
        class TestModel(Model):
            artist_name = fields.CharField()
            birth_date = fields.DateField(db_column='birth')
            death_date = fields.DateField(db_column='death')

        self.assertEqual(TestModel.db_column_to_attr_name('artist_name'), 'artist_name')
        self.assertEqual(TestModel.db_column_to_attr_name('birth'), 'birth_date')
        self.assertEqual(TestModel.db_column_to_attr_name('death'), 'death_date')

    def test_250_025_model_class_db_column_to_attr(self):
        class TestModel(Model):
            artist_name = fields.CharField()
            birth_date = fields.DateField(db_column='birth')
            death_date = fields.DateField(db_column='death')

        self.assertIsNone(TestModel.db_column_to_attr_name('published'))

    def test_250_030_model_class_db_fields(self):
        class TestModel(Model):
            artist_name = fields.CharField()
            birth_date = fields.DateField(db_column='birth')
            death_date = fields.DateField(db_column='death')

        self.assertCountEqual([f for f in TestModel.db_fields()],
                                [('artist_name', TestModel.artist_name),
                                 ('id',TestModel.id),                   # Auto generated
                                 ('birth_date', TestModel.birth_date),
                                 ('death_date', TestModel.death_date), ],
                              )

    def test_250_040_model_class_primaries(self):
        class TestModel(Model):
            artist_name = fields.CharField()
            birth_date = fields.DateField(db_column='birth')
            death_date = fields.DateField(db_column='death')

        self.assertEqual(TestModel.primary_field(),TestModel.id)

    def test_250_045_model_class_primary_explicit(self):
        class TestModel(Model):
            artist_name = fields.CharField(primary=True)
            birth_date = fields.DateField(db_column='birth')
            death_date = fields.DateField(db_column='death')

        self.assertEqual(TestModel.primary_field(),TestModel.artist_name)
        self.assertCountEqual([f for f in TestModel.db_fields()],
                                [('artist_name', TestModel.artist_name),
                                 ('birth_date', TestModel.birth_date),
                                 ('death_date', TestModel.death_date), ],
                              )

    def test_250_045_model_class_primary_error_non_primary_id(self):
        """Test that no 'id' field exists, and no primary key exists either"""
        with self.assertRaisesRegex(
                expected_exception=exceptions.PrimaryKeyError,
                expected_regex='Primary Key Error: \'id\' field exists but is not the primary key'):
            class TestModel(Model):
                id = fields.IntegerField()
                artist_name = fields.CharField()
                birth_date = fields.DateField(db_column='birth')
                death_date = fields.DateField(db_column='death')

    def test_250_046_model_class_primary_error_non_primary_id(self):
        """Test that no 'id' field exists, and no primary key exists either"""
        with self.assertRaisesRegex(
                expected_exception=exceptions.PrimaryKeyError,
                expected_regex='Primary Key Error: More than one primary field \(\'id\',\'artist_name\'\) defined in this Model'):
            class TestModel(Model):
                id = fields.IntegerField(primary=True)
                artist_name = fields.CharField(primary=True)
                birth_date = fields.DateField(db_column='birth')
                death_date = fields.DateField(db_column='death')

    def test_250_050_model_class_field_model_attribute(self):
        """Test that the model attribute is set correctly"""
        class TestModel(Model):
            artist_name = fields.CharField()
            birth_date = fields.DateField()
            death_date = fields.DateField()

        self.assertIs(TestModel.id.model, TestModel)
        self.assertIs(TestModel.artist_name.model, TestModel)
        self.assertIs(TestModel.birth_date.model, TestModel)
        self.assertIs(TestModel.death_date.model, TestModel)



# -----------------------------------------------------------------
#
# Test that a model instance with a single field can be created correctly
#
# ----------------------------------------------------------------
def test_basic_model_creation_wrapper(index, field_type=fields.CharField):
    class TestModel(Model):
        test_field = field_type()

    def test_basic_model_creation(self):
        """Test that we can create a model with a single field and that an attribute is created"""
        model_inst = TestModel()

        if field_type != fields.AutoField:
            self.assertTrue(hasattr(model_inst, 'id'))
        self.assertTrue(hasattr(model_inst, 'test_field'))

    return test_basic_model_creation


@GenerateTestMethods(test_name='ModelCreation',
                     test_method=test_basic_model_creation_wrapper,
                     test_cases=[
                         {'field_type': fields.AutoField},
                         {'field_type': fields.BinaryField},
                         {'field_type': fields.BooleanField},
                         {'field_type': fields.CharField},
                         {'field_type': fields.DateField},
                         {'field_type': fields.DateTimeField},
                         {'field_type': fields.DecimalField},
                         {'field_type': fields.EmailField},
                         {'field_type': fields.FloatField},
                         {'field_type': fields.FileField},
                         {'field_type': fields.IntegerField},
                         # ToDO Test ForeignField, FileField, Other Mappings
                     ],
                     method_name_template='test_251_{index:03d}_{test_name}_{test_data[field_type].__name__}',
                     method_doc_template='test_251_{index:03d} {test_name} {test_data[field_type].__name__}')
class TestModelCreation(unittest.TestCase):
    def setUp(self):
        pass



# -----------------------------------------------------------------
#
# Test that a model with a single field with default values are used correctly
#
# ----------------------------------------------------------------
def test_basic_model_creation_with_defaults_wrapper(index,
                                                    field_type=fields.CharField,
                                                    default=None):
    class TestModel(Model):
        test_field = field_type(default=default)

    def test_basic_model_creation_with_defaults(self):
        """Test that we can create a model with a single field and that the default value is used correctly"""
        model_inst = TestModel()

        self.assertTrue(hasattr(model_inst, 'test_field'))
        self.assertEqual(model_inst.test_field, default)

    return test_basic_model_creation_with_defaults


@GenerateTestMethods(test_name='ModelCreationDefaults',
                     test_method=test_basic_model_creation_with_defaults_wrapper,
                     test_cases=[
                         {'field_type': fields.BinaryField,
                          'default': bytearray([1, 2, 3]), },
                         {'field_type': fields.BooleanField,
                          'default': True, },
                         {'field_type': fields.CharField,
                          'default': 'Hello', },
                         {'field_type': fields.DateField,
                          'default': date(year=2017, month=8, day=17), },
                         {'field_type': fields.DateTimeField,
                          'default': datetime(year=2017, month=8, day=17,
                                              hour=15, minute=23,
                                              second=12), },
                         {'field_type': fields.DecimalField,
                          'default': Decimal('13.5'), },
                         {'field_type': fields.DurationField,
                          'default': timedelta(days=3, seconds=17), },
                         {'field_type': fields.EmailField,
                          'default': 'tony@abc.com', },
                         {'field_type': fields.FloatField, 'default': 1.75, },
                         {'field_type': fields.IntegerField, 'default': 113, },
                         # ToDO Test ForeignField, FileField, Other Mappings
                     ],
                     method_name_template='test_252_{index:03d}_{test_name}_{test_data[field_type].__name__}',
                     method_doc_template='test 252_{index:03d} {test_name} {test_data[field_type].__name__}')
class TestModelCreationDefaults(unittest.TestCase):
    def setUp(self):
        pass


# -----------------------------------------------------------------
#
# Test that a model with a single field that creation attributes override defaults
#
# ----------------------------------------------------------------
def test_basic_model_creation_with_attribute_setting_wrapper(index,
                                                             field_type=fields.CharField,
                                                             default=None,
                                                             value=None):
    class TestModel(Model):
        test_field = field_type(default=default)

    def test_basic_model_creation_with_attribute_setting(self):
        """Test that we can create a model with a single field and that the default value is used correctly"""
        model_inst = TestModel()

        self.assertTrue(hasattr(model_inst, 'test_field'))
        self.assertEqual(model_inst.test_field, default)

        model_inst.test_field = value

        self.assertEqual(model_inst.test_field, value)

    return test_basic_model_creation_with_attribute_setting


@GenerateTestMethods(test_name='ModelCreationOverwrite',
                     test_method=test_basic_model_creation_with_attribute_setting_wrapper,
                     test_cases=[
                         {'field_type': fields.BinaryField,
                          'value': bytearray([3, 2, 1]),
                          'default': bytearray([1, 2, 3]), },
                         {'field_type': fields.BooleanField, 'value': False,
                          'default': True, },
                         {'field_type': fields.CharField, 'value': 'Goodbye',
                          'default': 'Hello', },
                         {'field_type': fields.DateField,
                          'value': date(year=2017, month=1, day=1),
                          'default': date(year=2017, month=8, day=17), },
                         {'field_type': fields.DateTimeField,
                          'value': datetime(year=2017, month=1, day=11, hour=9,
                                            minute=5, second=35),
                          'default': datetime(year=2017, month=8, day=17,
                                              hour=15, minute=23,
                                              second=12), },
                         {'field_type': fields.DecimalField,
                          'value': Decimal(12.75),
                          'default': Decimal('13.5'), },
                         {'field_type': fields.DurationField,
                          'value': timedelta(days=5, seconds=11),
                          'default': timedelta(days=3, seconds=17), },
                         {'field_type': fields.EmailField,
                          'value': 'tony@def.com',
                          'default': 'tony@abc.com', },
                         {'field_type': fields.FloatField, 'value': -11.3,
                          'default': 1.75, },
                         {'field_type': fields.IntegerField, 'value': 516,
                          'default': 113, },
                         # ToDO Test ForeignField, FileField, Other Mappings
                     ],
                     method_name_template='test_253_{index:03d}_{test_name}_{test_data[field_type].__name__}',
                     method_doc_template='test_253_{index:03d} {test_name} {test_data[field_type].__name__}')
class TestModelCreationOverwriteDefaults(unittest.TestCase):
    def setUp(self):
        pass


#
# Same data is used to test both Model creation Errors and field setting errors
#
data_for_error_case = [
    {'case_name': 'Honour_null_false', 'field_type': fields.BooleanField,
     'field_kwargs': {'default': True, 'null': False},
     'creation_kwargs': {'test_field': None},
     'exception_regex': 'Invalid value for field \'test_field\': value is None, but \'null\' attribute is False'
     },
    {'case_name': 'Honour_null_false', 'field_type': fields.CharField,
     'field_kwargs': {'default': 'Hello', 'null': False},
     'creation_kwargs': {'test_field': None},
     'exception_regex': 'Invalid value for field \'test_field\': value is None, but \'null\' attribute is False'
     },
    {'case_name': 'Honour_blank_false', 'field_type': fields.CharField,
     'field_kwargs': {'default': 'Hello', 'blank': False},
     'creation_kwargs': {'test_field': ''},
     'exception_regex': 'Invalid value for field \'test_field\': value is blank/None, but \'blank\' attribute is False'
     },
    {'case_name': 'Honour_regex_validator', 'field_type': fields.CharField,
     'field_kwargs': {'default': 'Hello',
                      'validator': RegexValidator(r'[A-Z].*',
                                                  message='Must start with an uppercase letter')},
     'creation_kwargs': {'test_field': 'hello'},
     'exception_regex': 'Invalid value for field \'test_field\': Must start with an uppercase letter'
     },
    {'case_name': 'Honour_field_length', 'field_type': fields.CharField,
     'field_kwargs': {'default': 'Hello', 'max_length': 5},
     'creation_kwargs': {'test_field': 'hello there'},
     'exception_regex': 'Invalid value for field \'test_field\': value is longer than specified max_length 5'
     },
    {'case_name': 'Honour_null_false', 'field_type': fields.DateField,
     'field_kwargs': {'default': date(1, 1, 1), 'null': False},
     'creation_kwargs': {'test_field': None},
     'exception_regex': 'Invalid value for field \'test_field\': value is None, but \'null\' attribute is False'
     },
    {'case_name': 'Honour_null_false', 'field_type': fields.DateTimeField,
     'field_kwargs': {'default': datetime(1, 1, 1, 13, 23, 9), 'null': False},
     'creation_kwargs': {'test_field': None},
     'exception_regex': 'Invalid value for field \'test_field\': value is None, but \'null\' attribute is False'
     },
    {'case_name': 'Honour_null_false', 'field_type': fields.DecimalField,
     'field_kwargs': {'default': Decimal(3.5), 'null': False},
     'creation_kwargs': {'test_field': None},
     'exception_regex': 'Invalid value for field \'test_field\': value is None, but \'null\' attribute is False'
     },
    {'case_name': 'Invalid_value_for_conversion',
     'field_type': fields.DecimalField,
     'field_kwargs': {'default': '17.6'},
     'creation_kwargs': {'test_field': '18.3.4'},
     'exception_regex': 'Invalid value for field \'test_field\': Unable to convert str to decimal : Invalid syntax'
     },
    {'case_name': 'Invalid_value_for_conversion',
     'field_type': fields.DecimalField,
     'field_kwargs': {'default': '17.6'},
     'creation_kwargs': {'test_field': (1, 2, 3, 4, 5)},
     'exception_regex': 'Invalid value for field \'test_field\': Unable to convert tuple to decimal : Invalid syntax'
     },
    {'case_name': 'Honor_null_false', 'field_type': fields.DurationField,
     'field_kwargs': {'default': timedelta(seconds=15), 'null': False},
     'creation_kwargs': {'test_field': None},
     'exception_regex': 'Invalid value for field \'test_field\': value is None, but \'null\' attribute is False'
     },
    {'case_name': 'Honour_null_false', 'field_type': fields.EmailField,
     'field_kwargs': {'default': 'tony@aabc.com', 'null': False},
     'creation_kwargs': {'test_field': None},
     'exception_regex': 'Invalid value for field \'test_field\': value is None, but \'null\' attribute is False'
     },
    {'case_name': 'Honor_blank_false', 'field_type': fields.EmailField,
     'field_kwargs': {'default': 'tony@abc.com', 'blank': False},
     'creation_kwargs': {'test_field': ''},
     'exception_regex': 'Invalid value for field \'test_field\': value is blank/None, but \'blank\' attribute is False'
     },
    {'case_name': 'Honour_regex_validator', 'field_type': fields.EmailField,
     'field_kwargs': {'default': 'tony@abc.com', },
     'creation_kwargs': {'test_field': 'tony@com'},
     'exception_regex': 'Invalid value for field \'test_field\': Invalid Email address'
     },
    {'case_name': 'Honor_null_false', 'field_type': fields.FloatField,
     'field_kwargs': {'default': 11.5, 'null': False},
     'creation_kwargs': {'test_field': None},
     'exception_regex': 'Invalid value for field \'test_field\': value is None, but \'null\' attribute is False'
     },
    {'case_name': 'Conversion_failure', 'field_type': fields.FloatField,
     'field_kwargs': {'default': '11.5'},
     'creation_kwargs': {'test_field': '19.1.3'},
     'exception_regex': 'Invalid value for field \'test_field\': Invalid value : could not convert string to float: \'19.1.3\''
     },
    {'case_name': 'Honour_null_false', 'field_type': fields.FloatField,
     'field_kwargs': {'default': 11.5, 'null': False},
     'creation_kwargs': {'test_field': None},
     'exception_regex': 'Invalid value for field \'test_field\': value is None, but \'null\' attribute is False'
     },
    {'case_name': 'Conversion_failure', 'field_type': fields.IntegerField,
     'field_kwargs': {'default': '11'},
     'creation_kwargs': {'test_field': '19.1'},
     'exception_regex': 'Invalid value for field \'test_field\': Invalid value : invalid literal for int\(\) with base 10: \'19.1\''
     },

    # ToDO Test ForeignField, FileField, Other Mappings
    ]


# -----------------------------------------------------------------
#
# Test that field validation errors are dealt with correctly
#
# ----------------------------------------------------------------
def test_basic_model_creation_with_errors_wrapper(index, case_name='',
                                                  field_type=fields.CharField,
                                                  field_kwargs=None,
                                                  creation_kwargs=None,
                                                  exception_regex=''):
    """Test that invalid values passed to the Instance constructor are caught and generate an error"""

    field_kwargs = field_kwargs if field_kwargs else None

    class TestModel(Model):
        test_field = field_type(**field_kwargs)

    creation_kwargs = creation_kwargs if creation_kwargs else None

    def test_basic_model_creation_with_errors(self: unittest.TestCase):
        """Test that we can create a model with a single field and that the default value is used correctly"""

        with self.assertRaisesRegex(AttributeError,
                                    expected_regex=exception_regex):
            model_inst = TestModel(**creation_kwargs)

    return test_basic_model_creation_with_errors


@GenerateTestMethods(test_name='ModelCreationWithErrors',
                     test_method=test_basic_model_creation_with_errors_wrapper,
                     test_cases=data_for_error_case,
                     method_name_template='test_254_{index:03d}_{test_name}_{test_data[field_type].__name__}_{test_data[case_name]}',
                     method_doc_template='test_254_{index:03d} {test_name} {test_data[field_type].__name__}')
class TestModelCreationErrors(unittest.TestCase):
    def setUp(self):
        pass


# -----------------------------------------------------------------
#
# Test that field validation errors are dealt with correctly
#
# ----------------------------------------------------------------
def test_basic_model_field_setting_with_errors_wrapper(index, case_name='',
                                                       field_type=fields.CharField,
                                                       field_kwargs=None,
                                                       creation_kwargs=None,
                                                       exception_regex=''):
    """Test that invalid values passed to the Instance constructor are caught and generate an error"""

    field_kwargs = field_kwargs if field_kwargs else None

    class TestModel(Model):
        test_field = field_type(**field_kwargs)

    creation_kwargs = creation_kwargs if creation_kwargs else None

    def test_basic_model_field_setting_with_errors(self: unittest.TestCase):
        """Test that we can create a model with a single field and that the default value is used correctly"""

        value = creation_kwargs['test_field']
        del creation_kwargs['test_field']
        model_inst = TestModel(**creation_kwargs)

        with self.assertRaisesRegex(AttributeError,
                                    expected_regex=exception_regex):
            model_inst.test_field = value

    return test_basic_model_field_setting_with_errors


@GenerateTestMethods(test_name='FieldSettingWithErros',
                     test_method=test_basic_model_field_setting_with_errors_wrapper,
                     test_cases=data_for_error_case,
                     method_name_template='test_255_{index:03d}_{test_name}_{test_data[field_type].__name__}_{test_data[case_name]}',
                     method_doc_template='test_255_{index:03d} {test_name} {test_data[field_type].__name__}')
class ModelFieldSettings(unittest.TestCase):
    def setUp(self):
        pass


class TestModelIdAttribute(unittest.TestCase):
    def setUp(self):
        pass

    def test_260_001_test_id_in_constructor(self):
        """Test that the model id attribute is set correctly within the constructor"""

        class TestModel(Model):
            artist_name = fields.CharField()
            birth_date = fields.DateField()
            death_date = fields.DateField()

        inst = TestModel(id=17, artist_name='John Lennon',
                         birth_date=date(year=1940,month=10,day=9),
                         death_date=date(year=1980,month=12,day=8))
        self.assertEqual(inst.id, 17)


    def test_260_002_test_id_in_constructor(self):
        """Test that the model id attribute can't be changed"""

        class TestModel(Model):
            artist_name = fields.CharField()
            birth_date = fields.DateField()
            death_date = fields.DateField()

        inst = TestModel(id=17, artist_name='John Lennon',
                         birth_date=date(year=1940, month=10, day=9),
                         death_date=date(year=1980, month=12, day=8))

        with self.assertRaises(AttributeError):
            inst.id = 18

    def test_260_003_test_id_not_in_constructor(self):
        """Test that the model attribute can't be set even if attribute isn't explicitly set in constructor"""

        class TestModel(Model):
            artist_name = fields.CharField()
            birth_date = fields.DateField()
            death_date = fields.DateField()

        inst = TestModel(artist_name='John Lennon',
                         birth_date=date(year=1940, month=10, day=9),
                         death_date=date(year=1980, month=12, day=8))

        with self.assertRaises(AttributeError):
            inst.id = 18

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
