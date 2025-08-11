# Generated manually for designer field update

from django.db import migrations, models
import django.db.models.deletion


def migrate_product_designers(apps, schema_editor):
    """Product의 designer 필드를 User에서 Designer로 마이그레이션"""
    Product = apps.get_model('manufacturing', 'Product')
    Designer = apps.get_model('accounts', 'Designer')
    
    for product in Product.objects.all():
        try:
            # 기존 User를 통해 Designer 찾기
            designer = Designer.objects.get(user=product.designer)
            # 임시로 designer_id 저장
            product.temp_designer_id = designer.id
            product.save()
        except Designer.DoesNotExist:
            # Designer가 없는 경우 제품 삭제 또는 기본값 설정
            print(f"Warning: No designer found for product {product.id}")


def reverse_migrate_product_designers(apps, schema_editor):
    """역방향 마이그레이션"""
    Product = apps.get_model('manufacturing', 'Product')
    Designer = apps.get_model('accounts', 'Designer')
    
    for product in Product.objects.all():
        if hasattr(product, 'temp_designer_id'):
            designer = Designer.objects.get(id=product.temp_designer_id)
            product.designer = designer.user
            product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('manufacturing', '0006_order_customer_contact_order_customer_email_and_more'),
        ('accounts', '0003_designer_factory_remove_user_user_type'),
    ]

    operations = [
        # 임시 필드 추가
        migrations.AddField(
            model_name='product',
            name='temp_designer_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        
        # 데이터 마이그레이션
        migrations.RunPython(migrate_product_designers, reverse_migrate_product_designers),
        
        # 기존 designer 필드 제거
        migrations.RemoveField(
            model_name='product',
            name='designer',
        ),
        
        # 새로운 designer 필드 추가 (Designer 모델 참조)
        migrations.AddField(
            model_name='product',
            name='designer',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='products',
                to='accounts.designer',
                verbose_name='디자이너'
            ),
            preserve_default=False,
        ),
        
        # 데이터 복원
        migrations.RunSQL(
            "UPDATE products SET designer_id = temp_designer_id WHERE temp_designer_id IS NOT NULL",
            reverse_sql="-- No reverse SQL needed"
        ),
        
        # 임시 필드 제거
        migrations.RemoveField(
            model_name='product',
            name='temp_designer_id',
        ),
    ]