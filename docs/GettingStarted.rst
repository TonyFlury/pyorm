===============
Getting Started
===============

Start here if you have never used pyorm - or you need a referesher. If you are familiar with pyorm, then

Your first pyorm Application
============================

After :doc:`Installing pyorm<Installation>` of pyorm, there are a number of steps required
to make your pyOrm application : You will need to execute these steps for every pyOrm application you start.


Step 1 - Initialise the Pyorm directory Structure
-------------------------------------------------

First it is neccessary to create the pyorm directory structure

.. code-block:: bash

    $ pyorm initialise

and follow the prompts to answer the questions needed to create the initial settings and directory structure.

Answering all the questions with their defaults will create a directory structure in the current directory::

    |
    +--settings.py
    |
    +--models
    |       |
    |       +--- models.py
    |
    +-- migrations


 - The **settings.py** file contains the required :doc:`settings` for the pyORM library.
 - The **models** directory contains the definitions of the various :term:``models` that your application needs
    A sample **models.py** file is provided to give an example of how models definitions are formatted
 - The **migrations** directory is initially empty, but will eventually contain :term`migration` scripts

Step 2 - Your first model
-------------------------

In your favourite code editor and open models.py

.. literalinclude::  ../pyorm/_cli/initialisation_samples/models.py

In pyorm, a :term:`Model` is equivalent to a table in your RDBMS (see :doc:`relationship to RDBMS` for details). The initial Sample model has two _fields a name field and a birthdate _fields, which are defined as a 'CharField' and a 'DateField' respectively. There are many other :term:`field <_fields>` type available to use, and there are a number of options available to customize how those _fields behave. More details available on within :docs:`_fields`.

With the exception of inheriting from Model, and having a number of attributes which are defined as _fields, the ``Person`` class is just like any other Python class. You can extend the python class as much as you wish, adding new methods and attributes as required, but for the moment lets leave the model as it is.

To see what this model can do - lets test the model within the Python Console

.. code-block:: bash

    $ python -m pyorm.console .

This intructs the Python console to start up with the pyorm environment, and use the settings file within the current directory. There are other options available : see :doc:`Pyorm Console` for details).

By default the pyorm console uses a temporary database so you can use the defualt options to test changes to your model without overwriting your live data.

After the Python console starts up, you will see a normal python prompt, which all your expected python functionality.

Lets test your model in the python console

.. code-block:: python-con

    >>> from models.models import Person
    >>> from _datetime import date
    >>> john = Person(name='John Lennon', date=date(year=2012, month=1, day=17))
    >>> paul = Person(name='Paul McCartney', date=date(year=2012, month=1, day=17))



