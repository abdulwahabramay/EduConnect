# Generated by Django 5.1.1 on 2024-10-03 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_discussionreply'),
    ]

    operations = [
        migrations.AddField(
            model_name='discussionreply',
            name='content_reply_to',
            field=models.TextField(blank=True, help_text='Specific content of the post being replied to', null=True),
        ),
    ]
