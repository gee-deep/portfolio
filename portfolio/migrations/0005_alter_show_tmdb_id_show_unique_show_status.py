# Generated by Django 5.1.6 on 2025-02-18 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0004_show_backdrop_url_show_cast_show_director_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='show',
            name='tmdb_id',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AddConstraint(
            model_name='show',
            constraint=models.UniqueConstraint(fields=('tmdb_id', 'status'), name='unique_show_status'),
        ),
    ]
