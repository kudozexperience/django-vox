from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_courier', '0006_django2'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='failedmessage',
            options={'verbose_name': 'failed message'},
        ),
        migrations.AlterModelOptions(
            name='sitecontact',
            options={'verbose_name': 'site contact'},
        ),
        migrations.AlterModelOptions(
            name='template',
            options={'verbose_name': 'template'},
        ),
        migrations.RemoveField(
            model_name='failedmessage',
            name='protocol',
        ),
        migrations.AddField(
            model_name='failedmessage',
            name='contact_name',
            field=models.CharField(
                default='unnamed', max_length=500,
                verbose_name='contact name'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='template',
            name='target',
            field=models.CharField(
                default='re',
                help_text='Who this message actually gets sent to.',
                max_length=103),
        ),
    ]
