from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_alter_service_icon'),
    ]

    operations = [
        migrations.RenameField(
            model_name="service",
            old_name="icon",
            new_name="imagelink",
        ),
        migrations.AlterField(
            model_name="service",
            name="imagelink",
            field=models.URLField(blank=True),
        ),
    ]
