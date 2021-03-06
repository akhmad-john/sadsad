# Generated by Django 3.1.7 on 2021-03-08 18:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('factory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('mat_id', models.CharField(max_length=18)),
                ('mat_name', models.CharField(blank=True, max_length=255, null=True)),
                ('unit', models.CharField(blank=True, max_length=128, null=True)),
                ('pro_id', models.CharField(blank=True, max_length=1, null=True)),
                ('proid_name', models.CharField(blank=True, max_length=128, null=True)),
                ('mat_type', models.CharField(blank=True, max_length=4, null=True)),
                ('mat_type_name', models.CharField(blank=True, max_length=128, null=True)),
                ('oldmaterial', models.CharField(blank=True, max_length=18, null=True)),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product_created', to=settings.AUTH_USER_MODEL)),
                ('factory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='factory.factory')),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('mat_id',),
                'unique_together': {('factory', 'mat_id')},
            },
        ),
        migrations.CreateModel(
            name='ProductGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('group_id', models.CharField(blank=True, max_length=4, null=True)),
                ('name', models.CharField(max_length=128)),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='productgroup_created', to=settings.AUTH_USER_MODEL)),
                ('factory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='productgroups', to='factory.factory')),
                ('products', models.ManyToManyField(blank=True, related_name='productgroups', to='product.Product')),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='productgroup_modified', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(blank=True, related_name='productgroups', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('name', 'factory')},
            },
        ),
    ]
