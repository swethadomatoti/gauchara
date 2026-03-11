from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('project', '0018_add_image_file_to_cause_real'),  # last applied migration
    ]

    operations = [
        migrations.AddField(
            model_name='cause',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
