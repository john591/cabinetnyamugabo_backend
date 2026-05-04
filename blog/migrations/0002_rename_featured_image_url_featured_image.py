import blog.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="post",
            old_name="featured_image_url",
            new_name="featured_image",
        ),
        migrations.AlterField(
            model_name="post",
            name="featured_image",
            field=models.ImageField(
                upload_to=blog.models.get_upload_post_images_file_name
            ),
        ),
    ]
