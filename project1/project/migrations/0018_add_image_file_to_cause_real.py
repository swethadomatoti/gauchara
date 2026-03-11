from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('project', '0017_category1_remove_post_featured_image_url_and_more'),  # last applied migration
    ]

    operations = [
        migrations.AddField(
            model_name='cause',
            name='image_file',
            field=models.ImageField(upload_to='uploads/', null=True, blank=True),
        ),
    ]
