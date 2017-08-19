#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of validators

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '17 Aug 2017'

from .exceptions import pyOrmVaidationError
import re

from abc import abstractmethod
from typing import Pattern, TypeVar, Iterable,Container, Union, Type

T = TypeVar('T')

class ValidatorBase():
    """ A validator class - each instance is initialised with the details of how to check a value
    
        Example:
        v = Validator(<details>)
        v(value)
    
        details : Depends on the type of validator
        value : The value to be validated.
        
        Calling the validator instance should raise pyorm.core.exceptions.pyOrmValidationError (by default) if the value doe not
        comply with the rules
    """
    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Initialise the validator class"""
        pass

    @abstractmethod
    def __call__(self, value):
        """Call the validator class with the value to checked as the argument
        
            :raises pyorm.core.exceptions.pyOrmValidationError: by default if the check fails
                    validators might override this for their own use but care is needed.
        """
        raise NotImplemented('__call__ method must be initialised by the sub-class')


REGEX = TypeVar('REGEX', str, '_Regex')
FLAGS = TypeVar('FLAGS', int, None)

class RegexValidator(ValidatorBase):
    def __init__(self, regex: REGEX = '.*',
                 exception_class: Type[Exception] = pyOrmVaidationError,
                 message:str = 'Invalid',
                 inverse_match: bool = False,
                 flags: FLAGS = None):
        """A Deffered validator to compare a string to a regular expression

        :param regex: Either a regular expression string, or a pre Compiled regular expression
        :type regex: REGEX
        :param exception_class: The exception to be raised if the validation fails
        :type exception_class: ClassVar[Exception]
        :param message: The message to be contained within the exception if it is raised
        :type message: str
        :param inverse_match: WHen set to False the validation fails if the input DOESN'T match the regular expression
                              WHen set to True the validation fails if the input DOES match the regular expression
        :type inverse_match: bool
        :param flags: Any re flags to be used with the regex
        :type flags: Union[int,None]
                                
        :raises: TypeError if flags are given but regex is NOT a string
        
        """
        super().__init__()
        self._regex = regex
        self._exc_class = exception_class
        self._inverse_match = inverse_match
        self._message = message

        if flags and not isinstance(self._regex, str):
            raise TypeError('If the flags are set, regex must be a regular expression string.') from None

        self._flags = flags if flags else 0

        if isinstance(self._regex, str):
            self._regex = re.compile(pattern=self._regex, flags=self._flags)

    def __call__(self, value:str):
        """Validate the input value agains the regex previously provided
        
            :param value: The string to be validated
            :type value:str
            
            :raises: Exception as provided by the exception_class argument (pyOrmValidationError as Default)
            
        """
        if not (self._inverse_match is not bool(self._regex.match(value))):
            raise self._exc_class(self._message) from None


class EmailValidator(RegexValidator):
    def __init__(self, message:str='Invalid Email address',
                        exception_class:Type[Exception]=pyOrmVaidationError):
        """Very Naive email address validator"""
        super().__init__(exception_class=exception_class, message=message,
                         regex=r'^[A-Za-z][a-zA-Z0-9._]*(?<!\.)@([a-zA-Z0-9_]*\.){1,}(?<=\.)[a-zA-z]{2,3}$')


class ChoiceValidator(ValidatorBase):
    def __init__(self, choices:Container[T] = None,
                 inverse_match:bool=False,
                 message:str='Not a valid choice',
                 exception_class:Type[Exception]=pyOrmVaidationError):
        """Simple validator to check that the given value is one of a choice"""
        if not choices:
            raise AttributeError('Must provide a valid range of choices')

        super().__init__()
        self._choices = choices if choices else set()
        self._exception = exception_class
        self._message = message
        self._inverse_match = inverse_match

    def __call__(self, value:T):
        if not(self._inverse_match is not (value in self._choices)):
            raise self._exception(self._message) from None


class ChainValidators(ValidatorBase):
    """Simple Derived class to make it easy to chain validators together"""
    def __init__(self, validators: Iterable[ValidatorBase]):
        super().__init__()
        self._validators = validators

    def __call__(self, value:T):
        for validator in self._validators:
            validator(value)