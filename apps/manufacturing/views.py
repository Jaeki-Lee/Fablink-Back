from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer, QuantityScheduleSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        serializer.save(designer=self.request.user)

    @action(detail=True, methods=['patch'], url_path='quantity-schedule')
    def update_quantity_schedule(self, request, pk=None):
        """수량 및 일정 업데이트"""
        try:
            product = self.get_object()
            serializer = QuantityScheduleSerializer(product, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': '수량 및 일정이 성공적으로 저장되었습니다.',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'message': '입력 데이터가 올바르지 않습니다.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Product.DoesNotExist:
            return Response({
                'message': '제품을 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)