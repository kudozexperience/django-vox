# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-22 15:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_vox', '0003_activity_stream'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inboxitem',
            name='json',
        ),
        migrations.AddField(
            model_name='inboxitem',
            name='actor_json',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='inboxitem',
            name='object_json',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='inboxitem',
            name='target_id',
            field=models.CharField(db_index=True, default='', max_length=2048,
                                   verbose_name='actor id'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inboxitem',
            name='target_json',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='inboxitem',
            name='name',
            field=models.CharField(blank=True, max_length=512,
                                   verbose_name='name'),
        ),
        migrations.AddField(
            model_name='inboxitem',
            name='summary',
            field=models.TextField(blank=True),
        ),
    ]
