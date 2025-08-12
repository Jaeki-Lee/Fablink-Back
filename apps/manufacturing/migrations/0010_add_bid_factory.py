# Generated manually for BidFactory model

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_designer_factory_remove_user_user_type'),
        ('manufacturing', '0009_add_request_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='BidFactory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_price', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='장당 가격')),
                ('expect_work_day', models.DateField(verbose_name='예상 납기일')),
                ('settlement_status', models.CharField(choices=[('pending', '대기중'), ('confirmed', '확인됨'), ('completed', '완료'), ('cancelled', '취소됨')], default='pending', max_length=20, verbose_name='주문 상태')),
                ('is_matched', models.BooleanField(default=False, verbose_name='낙찰 상태')),
                ('matched_date', models.DateField(blank=True, null=True, verbose_name='낙찰 일자')),
                ('factory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='accounts.factory', verbose_name='공장 ID')),
                ('request_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='manufacturing.requestorder', verbose_name='주문 번호')),
            ],
            options={
                'verbose_name': '공장 입찰',
                'verbose_name_plural': '공장 입찰들',
                'db_table': 'bid_factory',
            },
        ),
        migrations.AddConstraint(
            model_name='bidfactory',
            constraint=models.UniqueConstraint(fields=('factory', 'request_order'), name='unique_factory_request_order'),
        ),
    ]