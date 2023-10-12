# Generated by Django 4.2.4 on 2023-10-12 13:54

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_question_how_many_answer_for_this_ques_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplyForLeave',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reason_for_apply', models.CharField(max_length=250)),
                ('description', models.TextField()),
                ('attachment', models.FileField(upload_to='tacher_reasons')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.teacher')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
