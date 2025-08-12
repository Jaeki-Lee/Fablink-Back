# Generated manually for order model simplification

from django.db import migrations, models
import django.db.models.deletion


def delete_all_orders(apps, schema_editor):
    """모든 주문 데이터 삭제"""
    Order = apps.get_model('manufacturing', 'Order')
    Order.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('manufacturing', '0007_alter_product_designer'),
    ]

    operations = [
        # 모든 주문 데이터 삭제
        migrations.RunPython(delete_all_orders, migrations.RunPython.noop),
        
        # 기존 Order 모델 삭제
        migrations.DeleteModel(
            name='Order',
        ),
        
        # 새로운 간단한 Order 모델 생성
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='주문 번호')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='manufacturing.product', verbose_name='제품')),
            ],
            options={
                'verbose_name': '주문',
                'verbose_name_plural': '주문들',
                'db_table': 'orders',
            },
        ),
    ]