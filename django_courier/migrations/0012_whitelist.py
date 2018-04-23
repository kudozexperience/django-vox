from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_courier', '0011_notification_from_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitecontact',
            name='enable_filter',
            field=models.CharField(
                choices=[('blacklist', 'Blacklist'),
                         ('whitelist', 'Whitelist')],
                default='blacklist', max_length=10),
        ),
    ]
