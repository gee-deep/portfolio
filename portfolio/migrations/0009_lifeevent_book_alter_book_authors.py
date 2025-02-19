# Generated by Django 5.1.6 on 2025-02-19 18:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0008_rename_review_book_description_remove_book_author_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lifeevent',
            name='book',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='life_events', to='portfolio.book'),
        ),
        migrations.AlterField(
            model_name='book',
            name='authors',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
