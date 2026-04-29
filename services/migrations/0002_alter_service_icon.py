from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="icon",
            field=models.TextField(blank=True),
        ),
    ]
