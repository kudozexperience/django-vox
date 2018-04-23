from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_courier', '0010_sender_recipient_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='from_code',
            field=models.BooleanField(
                default=False, verbose_name='from code',
                help_text='True if the notification is defined in the '
                          'code and automatically managed'),
        ),
        migrations.RemoveField('notification', 'use_sender'),
        migrations.RemoveField('notification', 'sender_model'),
        migrations.RemoveField('notification', 'use_recipient'),
        migrations.RemoveField('notification', 'recipient_model'),
        migrations.AddField(
            model_name='notification',
            name='source_model',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=models.deletion.CASCADE,
                related_name='+', to='contenttypes.ContentType',
                verbose_name='source model'),
        ),
        migrations.AddField(
            model_name='notification',
            name='target_model',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=models.deletion.CASCADE,
                related_name='+', to='contenttypes.ContentType',
                verbose_name='target model'),
        ),
        migrations.RenameField('template', 'target', 'recipient'),
        migrations.AlterField(
            model_name='template',
            name='recipient',
            field=models.CharField(
                default='re', max_length=103, verbose_name='recipient',
                help_text='Who this message actually gets sent to.'),
        ),
    ]
