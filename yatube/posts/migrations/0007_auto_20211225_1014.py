# Generated by Django 2.2.9 on 2021-12-25 10:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20211225_0943'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['pub_date']},
        ),
    ]