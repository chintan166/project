# Generated by Django 4.2.17 on 2025-02-05 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='address',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='contact_number',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='is_approved',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
