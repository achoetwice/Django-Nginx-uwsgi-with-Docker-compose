# Generated by Django 2.2 on 2019-06-03 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_auto_20190603_0703'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='classschedules',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='transaction',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='vendorclasses',
            options={'managed': False},
        ),
        migrations.AlterField(
            model_name='guesttemporaryinfo',
            name='id',
            field=models.CharField(default='0c1c7d40', max_length=255, primary_key=True, serialize=False, unique=True),
        ),
    ]
