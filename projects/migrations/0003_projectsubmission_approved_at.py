# Generated by Django 5.1.6 on 2025-02-27 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_remove_projectsubmission_submitted_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectsubmission',
            name='approved_at',
            field=models.DateTimeField(blank=True, help_text='Timestamp when client approves project task and payout to freelancer', null=True),
        ),
    ]
