# Generated by Django 5.0.7 on 2024-08-13 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_frame_frame_path_alter_video_video_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='frame',
            name='video',
        ),
        migrations.DeleteModel(
            name='Context',
        ),
        migrations.DeleteModel(
            name='Frame',
        ),
        migrations.DeleteModel(
            name='Video',
        ),
    ]
