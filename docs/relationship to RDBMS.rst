=========================================
Relationship between pyORM and your RDBMS
=========================================

There is a direct one to one relationship between classes, _fields, instances and relationships and data structures within a relational database :

============================== ================================
    pyOrm construct             Relational Database construct
============================== ================================
      Models                         Tables
      Fields                         Columns
   Field Attributes               Column Constraints
   Model instances                 Rows in Tables
 Mappings between Models        Joins and Keys between Tables
============================== ================================

Using these Models, _fields, and relationships, the application will be able to build :ref:`QuerySets` which in most cases remove the need for the application writer
to create SQL statements, since pyORM takes care of ALL of