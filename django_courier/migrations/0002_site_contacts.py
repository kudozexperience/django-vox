# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-01 06:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_courier', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteContact',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=500)),
                ('protocol', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'site contact',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='SiteContactPreference',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField()),
                ('notification', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='django_courier.Notification')),
                ('site_contact', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='django_courier.SiteContact')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='contact',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='contact',
            name='user',
        ),
        migrations.AddField(
            model_name='template',
            name='send_to_site_contacts',
            field=models.BooleanField(
                default=False,
                help_text='Whether this message is sent to the site contacts or '
                          'to the notification recipient.'),
        ),
        migrations.DeleteModel(
            name='Contact',
        ),
        migrations.AlterUniqueTogether(
            name='sitecontact',
            unique_together=set([('address', 'protocol')]),
        ),
    ]
