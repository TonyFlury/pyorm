==================
Adding comparisons
==================

A field comparison is the final element in a pyorm field lookup; it states what form of comparison should be executed - instance

``person__name__contains = 'Tony'``

checks that the field ``person.name`` contains the text ``Tony``. See the documentation on :doc:``QuerySets`` for more information.

While pyorm provides a number of comparisons it is entirely possible for your application to add new comparisons:

Step 1 - The Comparison function
--------------------------------

A comparison function is a python function which returns a correctly formated SQL fragment - it is passed two arguments, the ``field`` and the ``value``.
Using the lookup of ``person__name__contains = 'Tony'`` as an example :

  - ``field_name`` will be 'person.name' (Note that the double underscores have been converted to dots)
  - ``value`` will be 'Tony` - i.e. the value being compared with.

A simple Python function for the ``contains`` comparison would be :

.. code-block:: python

    def contain_comparison(field, value):
        return field + ' like \'%' + value + '%\''

In our example this function will create an sql fragment of :

        person.name like '%Tony%'

Step 2 - Register this comparison
---------------------------------

You now register your comparison function so that the pyorm database engine knows how to convert the field loop into an SQL clause. For this use the
''RegisterComparison'' decorator. You will also need to specify which engine class your comparison function applies to; since the SQL your function generate might be vendor specific. A full example which would the sqlite engine :

.. code-block:: python

    from pyorm.db.engine.utils import RegisterComparison
    from pyorm db.engine.sqliter import Engine

    @RegisterComparison(Engine, contains)
    def contain_comparison(field, value):
        return field + ' like \'%' + value + '%\''

It also possible to extend pyorm with :doc:``field functions <Adding functions>`` which another part of the field lookup syntax.


