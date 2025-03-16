# Generated by Django 5.1.6 on 2025-03-16 20:27

import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InspirationalQuote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quote', models.TextField()),
                ('speaker', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=15, validators=[django.core.validators.RegexValidator('^\\+?234\\d{10}$', 'Invalid phone number format. Please use +234XXXXXXXXXX.')])),
                ('email', models.EmailField(max_length=254)),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('confirmed', models.BooleanField(default=False)),
                ('department', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Leader',
            fields=[
                ('worker', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='core.worker')),
                ('image', models.ImageField(default='leaders/default.png', upload_to='leaders/')),
            ],
        ),
    ]
