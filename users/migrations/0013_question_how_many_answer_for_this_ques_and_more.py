# Generated by Django 4.2.4 on 2023-10-11 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_alter_answer_options_alter_batch_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='how_many_answer_for_this_ques',
            field=models.IntegerField(default=4),
        ),
        migrations.AddField(
            model_name='quizcategory',
            name='duration',
            field=models.IntegerField(default=5),
        ),
    ]
