# Generated by Django 4.2.17 on 2025-02-05 11:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_product_image_product_rating_product_review_count_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='stock',
        ),
    ]
