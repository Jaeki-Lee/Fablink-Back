import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db import transaction
from .models import Product, Order, RequestOrder
from .serializers import ProductSerializer, ProductCreateSerializer, OrderSerializer, OrderCreateSerializer

logger = logging.getLogger(__name__)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer
    
    def get_queryset(self):
        # 디자이너는 자신의 제품만, 공장주는 모든 제품 조회 가능
        if hasattr(self.request.user, 'designer'):
            return Product.objects.filter(designer=self.request.user.designer)
        return Product.objects.all()

    def perform_create(self, serializer):
        # 디자이너만 제품 생성 가능
        if not hasattr(self.request.user, 'designer'):
            return Response(
                {'error': '디자이너만 제품을 생성할 수 있습니다.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(designer=self.request.user.designer)
    
    def create(self, request, *args, **kwargs):
        logger.info(f"Product create request from user: {request.user}")
        logger.info(f"Request data: {request.data}")
        
        # 디자이너 권한 확인
        if not hasattr(request.user, 'designer'):
            logger.warning(f"Non-designer user attempted to create product: {request.user}")
            return Response(
                {'error': '디자이너만 제품을 생성할 수 있습니다.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer validation errors: {serializer.errors}")
            return Response(
                {'error': 'Validation failed', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            self.perform_create(serializer)
            logger.info(f"Product created successfully: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            return Response(
                {'error': 'Failed to create product', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def get_queryset(self):
        # 디자이너는 자신의 제품에 대한 주문만 조회 가능
        if hasattr(self.request.user, 'designer'):
            return Order.objects.filter(product__designer=self.request.user.designer)
        # 공장주는 모든 주문 조회 가능
        return Order.objects.all()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_manufacturing(request):
    """
    단일 제출 엔드포인트: Product -> Order -> RequestOrder 생성.
    - 요구 권한: 디자이너
    - 입력: multipart/form-data 권장. 파일 필드는 image_path(선택).
    - 응답: { product_id, order_id, request_order_id }
    """
    try:
        # 디자이너 권한 확인
        if not hasattr(request.user, 'designer'):
            return Response({'detail': '디자이너만 제출할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data

        # 필드 매핑 및 전처리
        name = data.get('name')
        season = data.get('season')
        target = data.get('target') or data.get('target_customer')
        concept = data.get('concept')
        detail = data.get('detail')
        size = data.get('size')
        quantity_raw = data.get('quantity')
        fabric_code = data.get('fabric_code')
        material_code = data.get('material_code')
        due_date = data.get('due_date')
        memo = data.get('memo')
        image_file = request.FILES.get('image_path')

        # 유효성 최소 체크
        required = {'name': name, 'season': season, 'target': target, 'concept': concept}
        missing = [k for k, v in required.items() if not v]
        if missing:
            return Response({'detail': f"필수 값 누락: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        # 수량 정수 변환
        quantity = None
        if quantity_raw not in (None, ''):
            try:
                quantity = int(quantity_raw)
            except ValueError:
                return Response({'detail': 'quantity는 정수여야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        fabric = {'name': fabric_code} if fabric_code else None
        material = {'name': material_code} if material_code else None

        with transaction.atomic():
            product = Product(
                designer=request.user.designer,
                name=name,
                season=season,
                target=target,
                concept=concept,
                detail=detail or '',
                size=size or None,
                quantity=quantity,
                fabric=fabric,
                material=material,
                due_date=due_date or None,
                memo=memo or '',
            )
            if image_file:
                product.image_path = image_file
            product.save()

            order = Order.objects.create(product=product)

            request_order = RequestOrder.objects.create(
                order=order,
                designer_name=str(request.user._obj.name if hasattr(request.user, '_obj') else getattr(request.user, 'name', '')),
                product_name=product.name,
                quantity=product.quantity or 0,
                due_date=product.due_date or None,
            )

        return Response({
            'product_id': product.id,
            'order_id': order.order_id,
            'request_order_id': request_order.id,
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception('submit_manufacturing error')
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)