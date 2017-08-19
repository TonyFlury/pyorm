#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of _core

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
__created__ = '25 Jul 2017'

import click
import sys
from os import mkdir
from shutil import copy
from pathlib import Path



class BaseProcess():
    """Mixin for all processes - define some basic methods common to all"""
    def __init__(self,verbosity=1, dry_run=False):
        self._verbosity = verbosity
        self._dry_run = dry_run

    def echo(self, level, msg, *args, **kwargs):
        """Standardised wrapper around click.echo"""
        if level <= self._verbosity:
            click.echo(msg, *args, **kwargs)

    def execute_cmd(self, cmd, *args, **kwargs):
        if not self._dry_run:
            return cmd(*args, **kwargs)

class Initialise(BaseProcess):
    """Initialisation process for applications - create folders and copy files"""
    def __init__(self, verbosity=1, dry_run=False, path='.'):

        super().__init__(verbosity=verbosity, dry_run=dry_run)

        self._path = path

    def execute(self):

        try:
            here = Path(__file__).parent

            self.echo(1, 'Creating \"models\" directory')
            self.execute_cmd(mkdir, str(self._path / 'models') )

            self.echo(1, 'Creating \"migrations\" directory')
            self.execute_cmd(mkdir, str(self._path / 'migrations'))

            self.echo(1, 'Creating sample \"models\models.py\" file')
            self.execute_cmd(copy, src = str(here / 'initialisation_samples' / 'models.py'),
                               dst = str(self._path / 'models'/ 'models.py'))

            self.echo(1, 'Creating sample \"settings.py\" file')
            self.execute_cmd(copy, src = str(here / 'initialisation_samples' / 'settings.py'),
                               dst = str(self._path / 'settings.py'))

        except (OSError,IOError) as exception:
            self.echo(0, msg=str(exception), err=True )
            sys.exit(1)
        except:
            self.echo(0, msg=str(sys.exc_info()), err=True)
            sys.exit(1)
        else:
            return 0