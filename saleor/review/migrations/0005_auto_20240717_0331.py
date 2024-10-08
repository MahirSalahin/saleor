# Generated by Django 3.2.25 on 2024-07-16 21:31

import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion
import saleor.core.utils.json_serializer


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0004_auto_20240715_2103'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['rating'], 'verbose_name': 'review', 'verbose_name_plural': 'reviews'},
        ),
        migrations.AddField(
            model_name='review',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, encoder=saleor.core.utils.json_serializer.CustomJsonEncoder, null=True),
        ),
        migrations.AddField(
            model_name='review',
            name='private_metadata',
            field=models.JSONField(blank=True, default=dict, encoder=saleor.core.utils.json_serializer.CustomJsonEncoder, null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='product',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='review',
            name='user',
            field=models.IntegerField(),
        ),
        migrations.CreateModel(
            name='ReviewMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(db_index=True, editable=False, null=True)),
                ('private_metadata', models.JSONField(blank=True, default=dict, encoder=saleor.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict, encoder=saleor.core.utils.json_serializer.CustomJsonEncoder, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='reviews')),
                ('alt', models.CharField(blank=True, max_length=250)),
                ('type', models.CharField(choices=[('IMAGE', 'An uploaded image or an URL to an image'), ('VIDEO', 'A URL to an external video')], default='IMAGE', max_length=32)),
                ('external_url', models.CharField(blank=True, max_length=256, null=True)),
                ('oembed_data', models.JSONField(blank=True, default=dict)),
                ('to_remove', models.BooleanField(default=False)),
                ('review', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='media', to='review.review')),
            ],
            options={
                'ordering': ('sort_order', 'pk'),
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='reviewmedia',
            index=django.contrib.postgres.indexes.GinIndex(fields=['private_metadata'], name='reviewmedia_p_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='reviewmedia',
            index=django.contrib.postgres.indexes.GinIndex(fields=['metadata'], name='reviewmedia_meta_idx'),
        ),
    ]
