# Generated by Django 3.2 on 2022-01-15 20:18

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0037_auto_20210125_1833'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100, verbose_name='адрес')),
                ('first_name', models.CharField(max_length=20, verbose_name='имя заказчика')),
                ('last_name', models.CharField(max_length=20, verbose_name='фамилия заказчика')),
                ('phonenumber', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='контактный телефон')),
            ],
            options={
                'verbose_name': 'заказ',
                'verbose_name_plural': 'заказы',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(verbose_name='количество')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foodcartapp.order', verbose_name='заказ')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foodcartapp.product', verbose_name='товар')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(related_name='orders', through='foodcartapp.OrderItem', to='foodcartapp.Product', verbose_name='товары'),
        ),
    ]
