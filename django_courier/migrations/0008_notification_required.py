from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_courier', '0007_migrations'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='required',
            field=models.BooleanField(
                default=False,
                help_text='If true, triggering the notification will throw an'
                          ' error if there is no available template/contact',
                verbose_name='required'),
        ),
    ]
