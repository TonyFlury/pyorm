===============
Getting Started
===============

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

Step 2 - Create your application models
---------------------------------------

In your favourite editor create the relevants models in the models directory, these models files can be called anything you want, so long as they exist in your **models** directory.

Step 3 - Create the migration scripts
--------------------------------------

Once your models are ready you can create the relevant :term:`migration scripts<migration script>` :

.. code-block:: bash

    pyorm migration create

This will create one a :term:`migration script` within the **migrations** directory.

Step 4 - Apply the migration scripts
------------------------------------

Assuming your application works after :doc:`testing` you can apply the migrations to your production database:

.. code-block:: bash

    pyorm migration apply

Your production database is now ready to roll



