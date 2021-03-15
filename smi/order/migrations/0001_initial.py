# Generated by Django 3.1.7 on 2021-03-08 18:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        ('zone', '0001_initial'),
        ('factory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TrashOrderClose',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('data', models.JSONField(blank=True, null=True)),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trashorderclose_created', to=settings.AUTH_USER_MODEL)),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trashorderclose_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='OrderCheck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('Success', 'Success'), ('Error', 'Error')], max_length=50)),
                ('message', models.TextField()),
                ('active', models.BooleanField(default=False)),
                ('sap_message', models.TextField(default='')),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordercheck_created', to=settings.AUTH_USER_MODEL)),
                ('factory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='factory.factory')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.product')),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordercheck_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('aufnr', models.CharField(blank=True, max_length=12, null=True)),
                ('psmng', models.DecimalField(blank=True, decimal_places=3, max_digits=13, null=True)),
                ('status', models.CharField(choices=[('Заказ создан в SMI', 'Заказ создан в SMI'), ('Заказ отправлен в SAP', 'Заказ отправлен в SAP'), ('Заказ успешно был создан SAP', 'Заказ успешно был создан SAP'), ('Заказ не создан SAP (Ошибка)', 'Заказ не создан SAP (Ошибка)'), ('EditError', 'EditError'), ('EditMesError', 'EditMesError'), ('Заказ отправлен в MES', 'Заказ отправлен в MES'), ('Заказ успешно был создан MES', 'Заказ успешно был создан MES'), ('Заказ не создан MES (Ошибка)', 'Заказ не создан MES (Ошибка)'), ('SmiError', 'SmiError'), ('SapError', 'SapError')], default='Заказ создан в SMI', max_length=50)),
                ('counter', models.DecimalField(blank=True, decimal_places=3, default=0.0, max_digits=13, null=True)),
                ('cycle', models.CharField(blank=True, max_length=128, null=True)),
                ('cycleunit', models.CharField(blank=True, max_length=128, null=True)),
                ('active', models.BooleanField(default=False)),
                ('order_date', models.DateTimeField(blank=True, null=True)),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_created', to=settings.AUTH_USER_MODEL)),
                ('factory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='factory.factory')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='product.product')),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_modified', to=settings.AUTH_USER_MODEL)),
                ('zone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='zone.zone')),
            ],
            options={
                'verbose_name': 'Create order',
                'verbose_name_plural': 'Create orders',
            },
        ),
        migrations.CreateModel(
            name='NeKonvOrderCloseReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('quantity', models.CharField(blank=True, max_length=128, null=True)),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nekonvorderclosereport_created', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='order.order')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.product')),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nekonvorderclosereport_modified', to=settings.AUTH_USER_MODEL)),
                ('zone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='zone.zone')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='NeKonvOrderClose',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('aufnr', models.CharField(blank=True, max_length=12, null=True)),
                ('quantity', models.CharField(blank=True, max_length=128, null=True)),
                ('status', models.CharField(blank=True, choices=[('Success', 'Success'), ('MesError', 'MesError'), ('Error', 'Error'), ('SmiError', 'SmiError')], max_length=50, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('data', models.JSONField(blank=True, null=True)),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nekonvorderclose_created', to=settings.AUTH_USER_MODEL)),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nekonvorderclose_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('message', models.JSONField(blank=True, null=True)),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='log_created', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='order.order')),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='log_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Create log',
                'verbose_name_plural': 'Create logs',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='KonvOrderClose',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ipaddress', models.CharField(blank=True, max_length=50, null=True)),
                ('p_number', models.CharField(blank=True, max_length=20, null=True)),
                ('serialnum', models.CharField(blank=True, max_length=5000, null=True)),
                ('status', models.CharField(blank=True, choices=[('Success', 'Success'), ('MesError', 'MesError'), ('Error', 'Error'), ('SmiError', 'SmiError'), ('TexError', 'TexError')], max_length=50, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('data', models.JSONField(blank=True, null=True)),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='konvorderclose_created', to=settings.AUTH_USER_MODEL)),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='konvorderclose_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
    ]