# Generated by Django 3.2.6 on 2021-08-04 21:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("tgbase", "0001_initial"),
        ("packages", "0001_squashed_0004_rustpackage"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrackedPythonPackage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "package",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="packages.pythonpackage"),
                ),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="tgbase.user")),
            ],
        ),
    ]
