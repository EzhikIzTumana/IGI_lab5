# Generated by Django 5.0.6 on 2024-06-04 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_remove_user_name_user_branch'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Branch',
            new_name='Department',
        ),
        migrations.RenameField(
            model_name='insurancepolicy',
            old_name='branch',
            new_name='department',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='branch',
            new_name='department',
        ),
    ]