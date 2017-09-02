======================================
pyORM: Flexible Django like Python ORM
======================================

.. toctree::
    :maxdepth: 2
    :hidden:

    Installation
    GettingStarted
    models
    _fields
    relations to RDBMS and SQL
    testing
    glossary

pyORM is a Object Relationship Manager library which is heavily inspired by Django models. The aim of pyORM is to provide an
easy to use capability to map python classes to a relational database, without the need for the application to implement SQL.

In summary an application using pyORM will have :

  - Model classes
  - Model classes have _fields which have a set of attributes, default values, and optional validators
  - Instances of model classes which can be created, changed, saved and deleted
  - Relationships between models by specifying certain _fields which are mappings to other _fields on other models.

These constructs are :doc:`directly related to constructs with the rdbms <relationship to RDMS and SQL>`, but in the majority of cases your application wont need to be concerned with the details of structure of your database, as pyORM deals with all of those datails.

.. note::
  Every care is taken to try to ensure that this code comes to you bug free.
  If you do find an error - please report the problem on :

    - `GitHub Issues`_
    - By email to : `Tony Flury`_



.. _Github Issues: http://github.com/TonyFlury/pyorm/issues/new
.. _Tony Flury : mailto:anthony.flury@btinternet.com?Subject=pyorm%20Error
