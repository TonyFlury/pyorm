#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Test Suite for test_validators.py

Summary : 
    <summary of module/class being tested>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    
Test Series:
    100 : Validators
"""
import sys
import inspect
import unittest
import click

import pyorm.core.validators as validators
from pyorm.core.exceptions import pyOrmVaidationError

import re

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '17 Aug 2017'


class TestRegexValidator(unittest.TestCase):
    def setUp(self):
        pass

    def test_100_000_regex_validator_match_pass(self):
        """Test that the regex validators with default arguments passes as expected"""
        v = validators.RegexValidator(regex=r'[A-Z].*')

        try:
            v('Hello world')
        except pyOrmVaidationError as exc:
            self.fail('Unexpected Validation error raised {}'.format(str(exc)))
        except BaseException as exc:
            self.fail('Unexpected exception raised: {}'.format(str(exc)))

    def test_100_001_regex_validator_match_fail(self):
        """Test that the regex validator fails a simple test as expected"""
        v = validators.RegexValidator(regex=r'[A-Z].*')

        with self.assertRaisesRegex( pyOrmVaidationError,'Invalid' ):
            v('hello world')

    def test_100_002_regex_validator_match_fail_exception_class(self):
        """Test that the regex validator can create an alternative exception"""
        v = validators.RegexValidator(regex=r'[A-Z].*', exception_class=AttributeError)

        with self.assertRaisesRegex( AttributeError,'Invalid' ):
            v('hello world')

    def test_100_003_regex_validator_inverse_match_pass(self):
        """Test that regex validator works as expected with inverse matching"""
        v = validators.RegexValidator(regex=r'[A-Z].*', inverse_match=True)

        try:
            v('hello world')
        except pyOrmVaidationError as exc:
            self.fail('Unexpected Validation error raised {}'.format(str(exc)))
        except BaseException as exc:
            self.fail('Unexpected exception raised: {}'.format(str(exc)))

    def test_100_004_regex_validator_message(self):
        """Test that regex validator will create an alternative message"""
        v = validators.RegexValidator(regex=r'[A-Z].*', message='Failed validation')

        with self.assertRaisesRegex( pyOrmVaidationError,'Failed validation' ):
            v('hello world')

    def test_100_005_regex_validator_flags(self):
        """Test regex validator flags are honoured"""

        # Test uses inverse match to prove that IgnoreCase is used correctly
        v = validators.RegexValidator(regex=r'[A-Z].*', flags=re.IGNORECASE, inverse_match=True)

        with self.assertRaisesRegex( pyOrmVaidationError,'Invalid' ):
            v('hello world')

    def test_100_006_precompiled_regex_validator_flags(self):
        """Test regex validator flags cause error if regex is pre-compiled"""
        with self.assertRaises(TypeError):
            # Test uses inverse match to prove that IgnoreCase is used correctly
            v = validators.RegexValidator(regex=re.compile(r'[A-Z].*'), flags=re.IGNORECASE)

class TestEmailValidator(unittest.TestCase):
    def setUp(self):
        pass

    def test_101_000_ValidEmail_simple_user_simple_host(self):
        """Test with a simple user part to the email"""
        v = validators.EmailValidator()
        try:
            v('tony@abc.com')
        except pyOrmVaidationError:
            self.fail('Unexpected validation Error')
        except BaseException as exc:
            self.fail('Unexpected exception raised : {}'.format(str(exc)))

    def test_101_001_ValidEmail_complex_user_simple_host(self):
        """Test with a more complex user part"""
        v = validators.EmailValidator()
        try:
            v('tony.flury@abc.com')
        except pyOrmVaidationError:
            self.fail('Unexpected validation Error')
        except BaseException as exc:
            self.fail('Unexpected exception raised : {}'.format(str(exc)))

    def test_101_002_ValidEmail_complex_host_part(self):
        """Test with a more complex user and complex host part"""
        v = validators.EmailValidator()
        try:
            v('tony.flury@abc.def.ghi.com')
        except pyOrmVaidationError:
            self.fail('Unexpected validation Error')
        except BaseException as exc:
            self.fail('Unexpected exception raised : {}'.format(str(exc)))

    def test_101_003_InValidEmail_invalid_user_minus_sign(self):
        """Test with an invalid user part - with a minus sign"""
        v = validators.EmailValidator()
        with self.assertRaisesRegex(pyOrmVaidationError,'Invalid Email address'):
            v('tony.-@abc.com')

    def test_101_004_InValidEmail_invalid_user_hash(self):
        """Test with an invalid user part - with a hash sign"""
        v = validators.EmailValidator()
        with self.assertRaisesRegex(pyOrmVaidationError,'Invalid Email address'):
            v('ton#y@abc.com')

    def test_101_005_InValidEmail_invalid_user_dot_before_at(self):
        """Test with an invalid user part - dot before @ sign"""
        v = validators.EmailValidator()
        with self.assertRaisesRegex(pyOrmVaidationError,'Invalid Email address'):
            v('tony.@abc.com')

    def test_101_006_InValidEmail_invalid_host_no_hostname(self):
        """Test with an invalid email - no host name"""
        v = validators.EmailValidator()
        with self.assertRaisesRegex(pyOrmVaidationError,'Invalid Email address'):
            v('tony@com')

    def test_101_007_InValidEmail_invalid_host_tld_only_1_char(self):
        """Test with an invalid email - tld too short"""
        v = validators.EmailValidator()
        with self.assertRaisesRegex(pyOrmVaidationError,'Invalid Email address'):
            v('tony@abc.c')

    def test_101_008_InValidEmail_invalid_host_tld_too_long(self):
        """Test with an invalid email - tld too long"""
        v = validators.EmailValidator()
        with self.assertRaisesRegex(pyOrmVaidationError,'Invalid Email address'):
            v('tony@abc.comm')

    def test_101_009_validEmail_alt_exception(self):
        """Test with an invalid email - alternate exception"""
        v = validators.EmailValidator(exception_class=AttributeError)
        with self.assertRaisesRegex(AttributeError,'Invalid Email address'):
            v('tony.@abc.com')

    def test_101_010_validEmail_alt_message(self):
        """Test with an invalid email - alternate message"""
        v = validators.EmailValidator(message='Invalid email provided')
        with self.assertRaisesRegex(pyOrmVaidationError,'Invalid email provided'):
            v('tony.@abc.com')


class TestChoicesValidator(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_102_000_simple_integer_choices(self):
        v = validators.ChoiceValidator(choices={0,1,2,3,4,5,6,7,8,9})
        try:
            v(1)
        except pyOrmVaidationError as exc:
            self.fail(msg='Unexpected validation raised : {}'.format(str(exc)))
        except BaseException as exc:
            self.fail(msg='Unexpected exception raised : {}'.format(str(exc)))

    def test_102_001_simple_string_choices(self):
        v = validators.ChoiceValidator(choices={'labourer','foreman','manager'})
        try:
            v('labourer')
        except pyOrmVaidationError as exc:
            self.fail(msg='Unexpected validation raised : {}'.format(str(exc)))
        except BaseException as exc:
            self.fail(msg='Unexpected exception raised : {}'.format(str(exc)))

    def test_102_002_empty_choices(self):
        with self.assertRaises(AttributeError):
            v = validators.ChoiceValidator(choices=[])

    def test_102_003_None_choices(self):
        with self.assertRaises(AttributeError):
            v = validators.ChoiceValidator(choices=None)

    def test_102_004_inverse_match(self):
        v = validators.ChoiceValidator(choices={0,1,2,3,4,5,6,7,8,9},inverse_match=True)

        with self.assertRaisesRegex(pyOrmVaidationError,'Not a valid choice'):
            v(1)


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
