# Generated by Django 4.2.4 on 2023-08-26 08:43

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Box",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now
                    ),
                ),
                ("updated_on", models.DateTimeField(auto_now=True)),
                ("length", models.DecimalField(decimal_places=2, max_digits=10)),
                ("breadth", models.DecimalField(decimal_places=2, max_digits=10)),
                ("height", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                "ordering": ("-created_on",),
            },
        ),
    ]
