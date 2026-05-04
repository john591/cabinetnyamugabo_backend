import team.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("team", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="teammember",
            old_name="photo_url",
            new_name="photo",
        ),
        migrations.AlterField(
            model_name="teammember",
            name="photo",
            field=models.ImageField(
                upload_to=team.models.get_upload_team_images_file_name
            ),
        ),
    ]
