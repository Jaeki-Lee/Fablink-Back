# Generated manually for RequestOrder model

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('manufacturing', '0008_simplify_order_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designer_name', models.CharField(max_length=20, verbose_name='디자이너 사용자 이름')),
                ('product_name', models.CharField(max_length=100, verbose_name='제품명')),
                ('quantity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='수량')),
                ('due_date', models.DateField(verbose_name='납기일')),
                ('work_sheet_path', models.FileField(upload_to='request_orders/worksheets/', verbose_name='작업지시서')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_orders', to='manufacturing.order', verbose_name='주문 번호')),
            ],
            options={
                'verbose_name': '주문 요청',
                'verbose_name_plural': '주문 요청들',
                'db_table': 'request_order',
            },
        ),
    ]