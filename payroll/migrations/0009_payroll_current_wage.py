# Generated by Django 2.0.6 on 2018-06-25 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0008_auto_20180625_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='payroll',
            name='current_wage',
            field=models.DecimalField(decimal_places=2, default=18, max_digits=6),
            preserve_default=False,
        ),
    ]
