# Generated by Django 3.1.7 on 2021-03-08 18:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('factory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Direction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('display_name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Indicator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('display_name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zonename', models.CharField(blank=True, max_length=128, null=True, verbose_name='Наименование склада')),
                ('zone_id', models.PositiveIntegerField(verbose_name='cклад номер')),
                ('head_panel', models.CharField(blank=True, max_length=20, null=True)),
                ('ip_address', models.CharField(blank=True, max_length=30, null=True, verbose_name='IP адрес')),
                ('p_number', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('p_name', models.CharField(blank=True, max_length=128, null=True)),
                ('final_point', models.BooleanField(default=False)),
                ('direction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='zone.direction')),
                ('factory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='zones', to='factory.factory', verbose_name='Завод')),
                ('indicator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='zone.indicator')),
            ],
            options={
                'ordering': ('zonename',),
                'unique_together': {('factory', 'zonename', 'zone_id', 'indicator', 'head_panel', 'ip_address', 'p_number')},
            },
        ),
    ]
