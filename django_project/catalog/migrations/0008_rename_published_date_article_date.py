# Generated by Django 5.0.6 on 2024-06-04 21:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_delete_news'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='published_date',
            new_name='date',
        ),
    ]
