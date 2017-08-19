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

@click.group('show', invoke_without_command=True)
@click.version_option(version=version.__version__, prog_name='pyOrm')
@click.pass_context
def show(ctx):
    """Show summaries of current status
    """
    if ctx.invoked_subcommand is None:
        click.secho('\n{prog} : Error No migrate command provided - Consult help page'.format(prog = ctx.obj.prog),
                     err=True, fg='red')
        click.secho('\n{prog} show --help\n'.format(prog = ctx.obj.prog), bold=True, err=True, fg='red')
        return

    click.echo('showing')

@show.command()
@click.pass_context
@click.option('--last/--full', '-l/-f', default=True, help='Show most recent or all migrations')
@click.option('--summary/--full', '-s/-f', default=True, help='Show Summary or detailed view')
def migrations(ctx, last, summary):
    """Show applied migrations
    """
    click.echo('showing migrations - {} in {}'.format('Last one only' if last else 'All of them',
                                                       'summary' if summary else 'detail'))

@show.command()
@click.pass_context
@click.option('--summary/--full', '-s/-f', default=True, help='Show Summary or detailed view')
def tables(ctx, summary):
    """Show applied migrations"""
    click.echo('showing tables in {}'.format('summary' if summary else 'detail'))