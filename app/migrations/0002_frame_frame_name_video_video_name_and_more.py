# Generated by Django 5.0.7 on 2024-08-01 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='frame',
            name='frame_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='video',
            name='video_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='frame',
            name='frame_path',
            field=models.FileField(upload_to='frames/'),
        ),
        migrations.AlterField(
            model_name='video',
            name='video_path',
            field=models.FileField(upload_to='videos/'),
        ),
    ]