#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of utils

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
import click

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '23 Jul 2017'


class AllowAliases(click.Group):

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: {}'.format(', '.join(sorted(matches))))


class Application_Info():
    def __init__(self, verbose=None):
        self._prog = 'pyorm'
        self._module_name = 'pyORM'
        self._verbose = verbose

    @property
    def prog(self):
        return self._prog

    @property
    def module_name(self):
        return self._module_name

    @property
    def verbose(self):
        return self._verbose

    @verbose.setter
    def verbose(self, level):
        self._verbose = level




def doc_modifier(**kwargs):
    """Simple decorator to allow paramterised __doc__ string
    
        Doesn't need functools.wraps as the function isn't replaced.
    """
    def wrapper(func):
        """Paramterise the __doc__ string of the decorated function"""
        func.__doc__ = func.__doc__.format(**kwargs)
        return func

    return wrapper