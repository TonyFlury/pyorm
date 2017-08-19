#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of show.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

from .. import version

import click

@click.group('data', invoke_without_command=True)
@click.version_option(version=version.__version__, prog_name='pyOrm')
@click.pass_context
def data(ctx):
    """Show summaries of current status
    """
    if ctx.invoked_subcommand is None:
        click.secho('\n{prog} : Error No migrate command provided - Consult help page'.format(prog = ctx.obj.prog),
                     err=True, fg='red')
        click.secho('\n{prog} data --help\n'.format(prog = ctx.obj.prog), bold=True, err=True, fg='red')
        return

    click.echo('Data Tools')

@data.command()
@click.pass_context
@click.option('--sql', '-s', 'format', flag_value='sql', help='Dump data as SQL commands')
@click.option('--json', '-j', 'format', flag_value='json', help='Dump data as JSON commands', default =True)
def dump(ctx, format):
    """Show applied migrations
    """
    click.echo('dumping data as {}'.format(format))