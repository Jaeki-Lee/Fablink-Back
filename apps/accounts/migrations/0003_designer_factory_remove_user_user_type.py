# Generated manually for user table separation

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def migrate_users_to_designer_factory(apps, schema_editor):
    """기존 User 데이터를 Designer/Factory 테이블로 이관"""
    User = apps.get_model('accounts', 'User')
    Designer = apps.get_model('accounts', 'Designer')
    Factory = apps.get_model('accounts', 'Factory')
    
    for user in User.objects.all():
        if hasattr(user, 'user_type'):
            if user.user_type == 'designer':
                Designer.objects.create(
                    user=user,
                    specialization='',
                    experience_years=0
                )
            elif user.user_type == 'factory':
                Factory.objects.create(
                    user=user,
                    company_name=user.name,
                    production_capacity=0,
                    specialties=[]
                )


def reverse_migrate_users(apps, schema_editor):
    """역방향 마이그레이션 - Designer/Factory 데이터를 User로 복원"""
    User = apps.get_model('accounts', 'User')
    Designer = apps.get_model('accounts', 'Designer')
    Factory = apps.get_model('accounts', 'Factory')
    
    # Designer 사용자들의 user_type을 'designer'로 설정
    for designer in Designer.objects.all():
        designer.user.user_type = 'designer'
        designer.user.save()
    
    # Factory 사용자들의 user_type을 'factory'로 설정
    for factory in Factory.objects.all():
        factory.user.user_type = 'factory'
        factory.user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_options'),
    ]

    operations = [
        # Designer 모델 생성
        migrations.CreateModel(
            name='Designer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('portfolio_url', models.URLField(blank=True, null=True, verbose_name='포트폴리오 URL')),
                ('specialization', models.CharField(blank=True, max_length=100, null=True, verbose_name='전문 분야')),
                ('experience_years', models.PositiveIntegerField(default=0, verbose_name='경력 년수')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='designer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'designer',
                'verbose_name': '디자이너',
                'verbose_name_plural': '디자이너들',
            },
        ),
        
        # Factory 모델 생성
        migrations.CreateModel(
            name='Factory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=100, verbose_name='회사명')),
                ('business_license', models.CharField(blank=True, max_length=50, null=True, verbose_name='사업자등록번호')),
                ('production_capacity', models.PositiveIntegerField(default=0, verbose_name='월 생산 가능량')),
                ('specialties', models.JSONField(default=list, verbose_name='전문 제품군')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='factory', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'factory',
                'verbose_name': '공장',
                'verbose_name_plural': '공장들',
            },
        ),
        
        # 데이터 마이그레이션
        migrations.RunPython(migrate_users_to_designer_factory, reverse_migrate_users),
        
        # user_type 필드 제거
        migrations.RemoveField(
            model_name='user',
            name='user_type',
        ),
    ]