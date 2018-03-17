# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    template_cls = apps.get_model("django_courier", "Template")
    db_alias = schema_editor.connection.alias
    template_cls.objects.using(db_alias).filter(
        send_to_site_contacts=True).update(target='si')


def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    template_cls = apps.get_model("django_courier", "Template")
    db_alias = schema_editor.connection.alias
    template_cls.objects.using(db_alias).filter(
        target='si').update(send_to_site_contacts=True)


class Migration(migrations.Migration):

    dependencies = [
        ('django_courier', '0003_failed_messages'),
    ]

    operations = [
        # uncomment to run on postgres
        # migrations.RunSQL('SET CONSTRAINTS ALL IMMEDIATE',
        #                   reverse_sql=migrations.RunSQL.noop),
        migrations.AddField(
            model_name='template',
            name='target',
            field=models.CharField(
                choices=[('re', 'Recipient'), ('si', 'Site Contacts'), ('se', 'Sender')],
                default='re', help_text='Who this message actually gets sent to.',
                max_length=2),
        ),
        migrations.RunPython(forwards_func, reverse_func),
        # migrate target data
        migrations.RemoveField(
            model_name='template',
            name='send_to_site_contacts',
        ),
        migrations.AlterField(
            model_name='failedmessage',
            name='address',
            field=models.CharField(max_length=500, verbose_name='address'),
        ),
        migrations.AlterField(
            model_name='failedmessage',
            name='backend',
            field=models.CharField(max_length=100, verbose_name='backend'),
        ),
        migrations.AlterField(
            model_name='failedmessage',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='created at'),
        ),
        migrations.AlterField(
            model_name='failedmessage',
            name='error',
            field=models.TextField(verbose_name='error'),
        ),
        migrations.AlterField(
            model_name='failedmessage',
            name='message',
            field=models.TextField(verbose_name='message'),
        ),
        migrations.AlterField(
            model_name='failedmessage',
            name='protocol',
            field=models.CharField(max_length=100, verbose_name='protocol'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='description',
            field=models.TextField(verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='use_recipient',
            field=models.BooleanField(verbose_name='use recipient'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='use_sender',
            field=models.BooleanField(verbose_name='use sender'),
        ),
        migrations.AlterField(
            model_name='sitecontact',
            name='address',
            field=models.CharField(max_length=500, verbose_name='address'),
        ),
        migrations.AlterField(
            model_name='sitecontact',
            name='protocol',
            field=models.CharField(max_length=100, verbose_name='protocol'),
        ),
        migrations.AlterField(
            model_name='sitecontactpreference',
            name='is_active',
            field=models.BooleanField(verbose_name='is active'),
        ),
        # uncomment to run on postgres
        # migrations.RunSQL('SET CONSTRAINTS ALL IMMEDIATE',
        #                   reverse_sql=migrations.RunSQL.noop),
    ]
