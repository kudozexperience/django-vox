from __future__ import unicode_literals

from django.db import migrations, models

import django_courier.models


class Migration(migrations.Migration):

    dependencies = [
        ('django_courier', '0004_template_targets'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='sitecontact',
            managers=[
                ('objects', django_courier.models.SiteContactManager()),
            ],
        ),
        migrations.AddField(
            model_name='sitecontact',
            name='name',
            field=models.CharField(blank=True, max_length=500,
                                   verbose_name='name'),
        ),
    ]
