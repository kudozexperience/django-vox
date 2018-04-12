from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_courier', '0009_subjects'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='recipient_model',
            field=models.CharField(
                blank=True, max_length=500, verbose_name='recipient model'),
        ),
        migrations.AddField(
            model_name='notification',
            name='sender_model',
            field=models.CharField(
                blank=True, max_length=500, verbose_name='sender model'),
        ),
    ]
