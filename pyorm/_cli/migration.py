#!/usr/bin/env python
# coding=utf-8
"""
# pyORM : Implementation of migrate.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""

from .utils import AllowAliases, Application_Info, doc_modifier

from click.core import Command, Argument

import click

@click.group('migration', invoke_without_command=True, cls=AllowAliases, short_help='Manage database migrations')
@click.pass_context
def migration(ctx):
    """Sub-commands to create, verify and apply migration scripts, based on the application models
    
      \b
      - create      based to the application models identify changes and create
                    migration scripts to change the database schema. Data migrations
                    can be manually added before application.
      - apply       apply recent migrations - this includes creating the relevant
                    database if neccessary
      - sql         show the SQL statements of the migrations to be applied. The
                    migrations are not applied.
      - rollback    rollback a single migration from the database; can only
                    rollback the most recent migration.
      - show        show all migrations applied to this database
    """
    if ctx.invoked_subcommand is None:
        click.secho('\n{prog} : Error No migrate command provided - Consult help page'.format(prog = ctx.obj.prog),
                     err=True, fg='red')
        click.secho('\n{prog} migration --help\n'.format(prog = ctx.obj.prog), bold=True, err=True, fg='red')
        return

@migration.command()
@click.argument('path', type=click.Path(exists=True,dir_okay=True, writable=True,
                                       readable=True, resolve_path=True),
                       metavar='PATH', default='.', required=False)
@click.option('--dry_run','-n', is_flag=True, default=False,
              help='Identify the changes to the models, but without creating migration scripts')
@doc_modifier(prog=Application_Info().prog)
@click.pass_context
def create(ctx, dry_run):
    """Create migration scripts based on models or changes to models
    
      The `{prog} migration create` command looks at all models and identifies
      all of the differences between the current database schema and any un-applied migrations
      and the current models.
      
      Migration files are then generated which contain the appropriate DDL
      (Data Definition Language) SQL statements to create, alter and drop Tables,
      Indexes and other elements of the Database Schema as required.
      
      Since it is impossible to automatically generate data migration scripts; as 
      no framework can predict what the application data requirements are; but within
      the migration scripts there are hooks are provided to ensure that the data
      migration scripts can be executed automatically as the schema migrations
      are applied.
      
      Each time the `{prog} migration create` command is invoked, and changes
      are detected, a new migration script with a unique ID is created. 
      
      Arguments: 
      
        PATH : The path of the application, which contains the settings.py file. 
               Optional and if omitted defaults to the current directory.
    """
    click.echo('Making migrations - please wait')



@migration.command()
@click.argument('path', type=click.Path(exists=True,dir_okay=True,
                                        file_okay=False, writable=True,
                                       readable=True, resolve_path=True),
                       metavar='PATH', default='.')
@click.pass_context
def apply(ctx):
    """Apply migrations to database"""
    click.echo('Executing migrations')


@migration.command()
@click.argument('path', type=click.Path(exists=True,dir_okay=True, writable=True,
                                       readable=True, resolve_path=True),
                       metavar='PATH', default='.')
@click.pass_context
def sql(ctx):
    """Show sql of a migration"""
    click.echo('Executing migrations')


@migration.command()
@click.argument('index', type=click.INT, metavar='INDEX')
@click.argument('path', type=click.Path(exists=True,dir_okay=True, writable=True,
                                       readable=True, resolve_path=True),
                       metavar='PATH', default='.')
@click.pass_context
def rollback(ctx, index, path):
    """Remove a migration from database"""
    click.echo("Remove migration")

@migration.command()
@click.argument('index', type=click.INT, metavar='INDEX')
@click.argument('path', type=click.Path(exists=True,dir_okay=True, writable=True,
                                       readable=True, resolve_path=True),
                       metavar='PATH', default='.')
@click.pass_context
def show(ctx, index, path):
    """show migration applied to the database"""
    click.echo("Show migrations")