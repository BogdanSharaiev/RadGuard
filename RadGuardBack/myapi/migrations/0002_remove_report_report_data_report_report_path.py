# Generated by Django 5.1.4 on 2024-12-20 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapi', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='report_data',
        ),
        migrations.AddField(
            model_name='report',
            name='report_path',
            field=models.CharField(default='reports/report.pdf', max_length=255),
            preserve_default=False,
        ),
    ]
