# Generated by Django 5.2.3 on 2025-07-15 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_country_address'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ['country'], 'verbose_name_plural': 'Countries'},
        ),
        migrations.RemoveIndex(
            model_name='country',
            name='account_cou_name_9d19bd_idx',
        ),
        migrations.RenameField(
            model_name='country',
            old_name='name',
            new_name='country',
        ),
        migrations.AddIndex(
            model_name='country',
            index=models.Index(fields=['country'], name='account_cou_country_d5b142_idx'),
        ),
    ]
