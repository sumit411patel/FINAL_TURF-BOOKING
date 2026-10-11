# Removes turf_images_table model – no longer used in the project.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('turf', '0016_login_is_banned_alter_login_user_type'),
    ]

    operations = [
        migrations.DeleteModel(
            name='turf_images_table',
        ),
    ]
