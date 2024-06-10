# Generated by Django 5.0.6 on 2024-06-09 20:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0015_remove_insurancerisk_insurance_object_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='insurable_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='catalog.insurableobject'),
        ),
        migrations.RemoveField(
            model_name='contract',
            name='insurance_risk',
        ),
        migrations.AddField(
            model_name='contract',
            name='insurance_risk',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='catalog.insurancerisk'),
        ),
    ]
