# Generated by Django 2.0.6 on 2018-06-22 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0006_auto_20180620_2225'),
    ]

    operations = [
        migrations.AddField(
            model_name='payroll',
            name='gross_total',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=6),
            preserve_default=False,
        ),
    ]
