from __future__ import unicode_literals

import django.db.models.deletion
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
        migrations.AlterField(
            model_name='notification',
            name='source_model',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='+', to='contenttypes.ContentType',
                verbose_name='source model'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='target_model',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='+', to='contenttypes.ContentType',
                verbose_name='target model'),
        ),
        migrations.AlterField(
            model_name='template',
            name='recipient',
            field=models.CharField(
                default='re', max_length=103, verbose_name='recipient',
                help_text='Who this message actually gets sent to.'),
        ),
    ]
