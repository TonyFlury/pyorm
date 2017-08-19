#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of main

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

import click

from .utils import AllowAliases, Application_Info, doc_modifier
from .data import data
from .migration import migration
from .show import show
from .. import version

from ._core import Initialise

from pathlib import Path
import sys


@click.group(name=Application_Info().prog, invoke_without_command=True, cls=AllowAliases,
             epilog='sub-commands can be abbreviated so long as the command remains unique')
@click.option('-v','--verbose', help='Level of output', count=True)
@click.version_option(version=version.__version__, prog_name='pyOrm')
@click.pass_context
@doc_modifier(program ='pyorm')
def main(ctx, verbose):
    """{program} Management command
    
        Creation, migration and reporting on application database. Essential for developing and updating
        pyorm based applications. It is essential to at least initialise the database, and then create
        and apply migrations based on the application models.
    
        The {program} command provides tools for managing the database including
      
        \b
        - Initial creation
        - Creation of SQL migration scripts for application models
        - Application of SQL migration scripts
        - Removal of SQL migrations
        - Database information including migration status
        - Lists of Tables
        - Summary of Tables and indexes
        
        for further help on the sub-commands enter: 
        
        {program} <sub-command> --help
        
    """
    ctx.obj = Application_Info(verbose=verbose)

    if ctx.invoked_subcommand is None:
        click.secho('\n{prog} : Error No command provided - Consult help page'.format(prog = ctx.obj.prog),
                     err=True, fg='red')
        click.secho('\n{prog} --help\n'.format(prog = ctx.obj.prog), bold=True, err=True, fg='red')
        return

    if not verbose:
        verbose = 1

    ctx.obj.verbose = verbose

    if verbose:
        click.echo('Now running at verbose mode {}'.format(verbose))

@main.command(short_help='Initialise application workspace')
@click.argument('path', type=click.Path(exists=True,
                                        dir_okay=True, file_okay=False,
                                        writable=True, readable=True, resolve_path=False),
                       metavar='PATH', default='.')
@click.option('--dry_run','-n', is_flag=True, default=False,
              help='Identify the changes to be made without executing them.')
@click.pass_context
@doc_modifier(prog=Application_Info().prog, module=Application_Info().module_name)
def initialise( ctx, path, dry_run):
    """Initialise the application database in the given path.
    
        If the PATH argument is omitted, the current directory is used as the PATH.
        
        The `{prog} initialise` command :
        
        \b
        - Creates a simple default 'settings.py' for the application.
        - A models directory with an sample model for your application
        - A migrations directory, initially empty.
      
        After `{prog} initialise` it is still necessary to create the database tables and 
        indexes required for the application. To do this use a combination of:
      
        \b
        - {prog} migration create - to create migration scripts based on the 
                                    application's model
        - {prog} migration apply - to apply those migrations to the database,
                                    creating the database as required
      
    """
    if not Path(path).is_dir():
        raise click.BadArgumentUsage('\"{}\" is not a directory'.format(path), ctx=ctx)

    click.echo('Initialising application in {} directory'.format(path))

    process = Initialise(verbosity=ctx.obj.verbose, dry_run=dry_run, path=Path(path))

    ret = process.execute()

    if ret == 0:
        sys.exit(0)
    else:
        click.echo('Aborted', err=True)

# Add migrate and show sub-commands
main.add_command(migration)
main.add_command(show)
main.add_command(data)