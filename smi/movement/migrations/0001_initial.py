# Generated by Django 3.1.7 on 2021-03-08 18:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('zone', '0001_initial'),
        ('factory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='IdCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('card_number', models.CharField(blank=True, max_length=20, null=True)),
                ('name', models.CharField(blank=True, max_length=128, null=True)),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='idcard_created', to=settings.AUTH_USER_MODEL)),
                ('factory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='id_cards', to='factory.factory')),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='idcard_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('factory', 'card_number')},
            },
        ),
        migrations.CreateModel(
            name='TransferLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('factory_from', models.CharField(blank=True, max_length=10, null=True)),
                ('factory_to', models.CharField(blank=True, max_length=10, null=True)),
                ('zone_from', models.CharField(blank=True, max_length=30, null=True)),
                ('zone_to', models.CharField(blank=True, max_length=30, null=True)),
                ('postingdate', models.CharField(blank=True, max_length=30, null=True)),
                ('requestdate', models.CharField(blank=True, max_length=30, null=True)),
                ('card_from', models.CharField(blank=True, max_length=20, null=True)),
                ('card_to', models.CharField(blank=True, max_length=20, null=True)),
                ('status', models.CharField(blank=True, choices=[('Success', 'Success'), ('Created', 'Created'), ('SapError', 'SapError'), ('MES_ERROR', 'MES_ERROR')], max_length=50, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transferlog_created', to=settings.AUTH_USER_MODEL)),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transferlog_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Mes Send Product Log',
                'verbose_name_plural': 'Mes Send Product Logs',
            },
        ),
        migrations.CreateModel(
            name='MovementLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('factory', models.CharField(blank=True, max_length=10, null=True)),
                ('zone', models.CharField(blank=True, max_length=30, null=True)),
                ('status', models.CharField(blank=True, choices=[('Success', 'Success'), ('SapError', 'SapError'), ('MesError', 'MesError')], max_length=50, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='movementlog_created', to=settings.AUTH_USER_MODEL)),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='movementlog_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Mes Get Product Log',
                'verbose_name_plural': 'Mes Get Product Logs',
            },
        ),
        migrations.CreateModel(
            name='LogMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('material', models.CharField(blank=True, max_length=128, null=True)),
                ('materialquan', models.CharField(blank=True, max_length=50, null=True)),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logmaterial_created', to=settings.AUTH_USER_MODEL)),
                ('transfer_log', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log_materials', to='movement.transferlog')),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logmaterial_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductMovement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('card_om', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='card_om_set', to='movement.idcard')),
                ('card_pm', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='card_pm_set', to='movement.idcard')),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='productmovement_created', to=settings.AUTH_USER_MODEL)),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='productmovement_modified', to=settings.AUTH_USER_MODEL)),
                ('zone_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zone_from_set', to='zone.zone')),
                ('zone_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zone_to_set', to='zone.zone')),
            ],
            options={
                'ordering': ('updated_at',),
                'unique_together': {('zone_from', 'card_om', 'zone_to', 'card_pm')},
            },
        ),
    ]
