# Generated by Django 3.2.6 on 2021-08-11 22:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tgbase", "0001_initial"),
        ("packages", "0001_squashed_0004_rustpackage"),
        ("tgbot", "0002_auto_20210804_2209"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrackedRustPackage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("chat", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="tgbase.chat")),
                ("package", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="packages.rustpackage")),
            ],
        ),
    ]
