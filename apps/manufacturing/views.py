import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Product, Order
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