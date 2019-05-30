# Generated by Django 2.2 on 2019-05-30 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0011_auto_20190530_0626'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TransactionCounterPay',
        ),
        migrations.AlterField(
            model_name='guesttemporaryinfo',
            name='id',
            field=models.CharField(default='afbe3b64', max_length=255, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='id',
            field=models.CharField(db_column='pk', default='734e3bac-9c58-46be-b959-c0b1e5', max_length=30, primary_key=True, serialize=False, unique=True),
        ),
    ]