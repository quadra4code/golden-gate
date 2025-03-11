# Generated by Django 5.1.5 on 2025-03-10 14:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInteraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('interaction_type', models.CharField(choices=[('view', 'View'), ('favorite', 'Favorite'), ('filter', 'Filter'), ('register', 'Register')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.city')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
