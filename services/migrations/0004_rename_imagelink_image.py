import services.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0003_remove_service_icon_service_imagelink"),
    ]

    operations = [
        migrations.RenameField(
            model_name="service",
            old_name="imagelink",
            new_name="image",
        ),
        migrations.AlterField(
            model_name="service",
            name="image",
            field=models.ImageField(
                upload_to=services.models.get_upload_service_images_file_name
            ),
        ),
    ]
