# Generated by Django 4.2.3 on 2023-08-07 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0014_alter_recipe_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='pic',
            field=models.BinaryField(),
        ),
    ]
