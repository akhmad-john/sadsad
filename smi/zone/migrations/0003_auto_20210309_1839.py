# Generated by Django 3.1.7 on 2021-03-09 18:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('zone', '0002_auto_20210309_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zone',
            name='direction',
            field=models.CharField(blank=True, choices=[('MS', 'From MES to SAP'), ('MS', 'From MES to TEX')], max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='zone',
            name='indicator',
            field=models.CharField(blank=True, choices=[('0', 'Не конвейерная зона'), ('1', 'Конвейерный зона')], max_length=32, null=True),
        ),
        migrations.CreateModel(
            name='ZoneFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('errors', models.JSONField(blank=True, null=True)),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='zonefile_created', to=settings.AUTH_USER_MODEL)),
                ('file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='zone_files', to='document.documentmodel')),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='zonefile_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
    ]
