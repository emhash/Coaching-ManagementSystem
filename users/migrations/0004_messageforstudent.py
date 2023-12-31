# Generated by Django 4.2.4 on 2023-10-06 13:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_messageforteacher'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageForStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('headline', models.CharField(max_length=250)),
                ('description', models.TextField()),
                ('upload_at', models.DateTimeField(auto_now_add=True)),
                ('visited', models.BooleanField()),
                ('message_for', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.student')),
            ],
        ),
    ]
