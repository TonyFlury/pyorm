from pyorm.db import migrations
from pyorm.db.models import fields

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewsletterSignUp',
            fields=[
                ('id', fields.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('migration_id',fields.CharField(max_length=40)),
                ('email', fields.EmailField(max_length=254)),
            ],
        ),
    ]
