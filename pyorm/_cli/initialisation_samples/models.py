from pyorm.db.models.models import Model
from pyorm.db.models.fields import CharField, DateField

class Person(Mode):
    name = CharField()
    birthdate = DateField()