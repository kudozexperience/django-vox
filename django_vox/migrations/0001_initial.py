# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-27 18:10
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models

import django_vox.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='FailedMessage',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('backend', models.CharField(
                    max_length=100, verbose_name='backend')),
                ('contact_name', models.CharField(
                    max_length=500, verbose_name='contact name')),
                ('address', models.CharField(
                    max_length=500, verbose_name='address')),
                ('message', models.TextField(verbose_name='message')),
                ('error', models.TextField(verbose_name='error')),
                ('created_at', models.DateTimeField(
                    auto_now_add=True, verbose_name='created at')),
            ],
            options={
                'verbose_name': 'failed message',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('codename', models.CharField(
                    max_length=100, verbose_name='codename')),
                ('description', models.TextField(
                    verbose_name='description')),
                ('required', models.BooleanField(
                    default=False,
                    help_text='If true, triggering the notification '
                              'will throw an error if there is no '
                              'available template/contact',
                    verbose_name='required')),
                ('from_code', models.BooleanField(
                    default=False,
                    help_text='True if the notification is defined in '
                              'the code and automatically managed',
                    verbose_name='from code')),
                ('content_type', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='contenttypes.ContentType',
                    verbose_name='content type')),
                ('source_model', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='+', to='contenttypes.ContentType',
                    verbose_name='source model')),
                ('target_model', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='+', to='contenttypes.ContentType',
                    verbose_name='target model')),
            ],
            managers=[
                ('objects', django_vox.models.NotificationManager()),
            ],
        ),
        migrations.CreateModel(
            name='SiteContact',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    blank=True, max_length=500, verbose_name='name')),
                ('protocol', models.CharField(
                    max_length=100, verbose_name='protocol')),
                ('address', models.CharField(
                    max_length=500, verbose_name='address')),
                ('enable_filter', models.CharField(
                    choices=[('blacklist', 'Blacklist'),
                             ('whitelist', 'Whitelist')],
                    default='blacklist', max_length=10)),
            ],
            options={
                'verbose_name': 'site contact',
            },
            managers=[
                ('objects', django_vox.models.SiteContactManager()),
            ],
        ),
        migrations.CreateModel(
            name='SiteContactSetting',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('enabled', models.BooleanField(verbose_name='enabled')),
                ('notification', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='django_vox.Notification')),
                ('site_contact', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='django_vox.SiteContact')),
            ],
            options={
                'verbose_name': 'site contact setting',
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('backend', models.CharField(
                    max_length=100, verbose_name='backend')),
                ('subject', models.CharField(
                    blank=True, max_length=500, verbose_name='subject')),
                ('content', models.TextField(verbose_name='content')),
                ('recipient', models.CharField(
                    default='re',
                    help_text='Who this message actually gets sent to.',
                    max_length=103, verbose_name='recipient')),
                ('enabled', models.BooleanField(
                    default=True,
                    help_text='When not active, the template will be ignored',
                    verbose_name='enabled')),
                ('notification', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='django_vox.Notification',
                    verbose_name='notification')),
            ],
            options={
                'verbose_name': 'template',
            },
        ),
        migrations.AlterUniqueTogether(
            name='sitecontact',
            unique_together={('address', 'protocol')},
        ),
        migrations.AlterUniqueTogether(
            name='sitecontactsetting',
            unique_together={('site_contact', 'notification')},
        ),
    ]