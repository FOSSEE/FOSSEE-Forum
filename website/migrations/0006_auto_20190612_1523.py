# Generated by Django 2.1.3 on 2019-06-12 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_auto_20181120_1231'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='answercomment',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='question',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
