import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db import transaction
from .models import Product, Order, RequestOrder, BidFactory
from .serializers import (
    ProductSerializer, ProductCreateSerializer, OrderSerializer, OrderCreateSerializer,
    RequestOrderSerializer, BidFactorySerializer, BidFactoryCreateSerializer
)

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_factory_orders(request):
    """
    공장주용 주문 목록 조회 - RequestOrder와 BidFactory 정보 포함
    """
    try:
        # 공장주 권한 확인
        if not hasattr(request.user, 'factory'):
            return Response({'detail': '공장주만 접근할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 모든 RequestOrder 조회 (pending 상태)
        request_orders = RequestOrder.objects.filter(status='pending').select_related(
            'order__product__designer'
        ).prefetch_related('bids__factory')
        
        orders_data = []
        for req_order in request_orders:
            # 해당 공장의 입찰 정보 확인
            factory_bid = req_order.bids.filter(factory=request.user.factory).first()
            
            # 디자이너 정보 가져오기
            designer = req_order.order.product.designer
            
            order_data = {
                'id': req_order.id,
                'orderId': req_order.order.order_id,
                'status': 'pending' if not factory_bid else 'responded',
                'createdAt': req_order.order.product.created_at,
                'quantity': req_order.quantity,
                'customerName': req_order.designer_name,
                'customerContact': designer.contact if designer.contact else '연락처 정보 없음',
                'shippingAddress': designer.address if designer.address else '주소 정보 없음',

                'notes': req_order.order.product.memo or '',
                'productInfo': {
                    'id': req_order.order.product.id,
                    'name': req_order.product_name,
                    'designerName': req_order.designer_name,
                    'season': req_order.order.product.season,
                    'target': req_order.order.product.target,
                    'concept': req_order.order.product.concept,
                    'detail': req_order.order.product.detail,
                    'size': req_order.order.product.size,
                    'fabric': req_order.order.product.fabric,
                    'material': req_order.order.product.material,
                    'dueDate': req_order.due_date,
                    'memo': req_order.order.product.memo,
                    'imageUrl': request.build_absolute_uri(req_order.order.product.image_path.url) if req_order.order.product.image_path else None,
                    'workSheetUrl': request.build_absolute_uri(req_order.work_sheet_path.url) if req_order.work_sheet_path else None,
                }
            }
            
            # 입찰 정보가 있으면 단가 정보 추가, 없으면 기본값 설정
            if factory_bid:
                order_data.update({
                    'unitPrice': factory_bid.work_price,
                    'totalPrice': factory_bid.work_price * req_order.quantity,
                    'bidId': factory_bid.id,
                    'estimatedDeliveryDays': (factory_bid.expect_work_day - req_order.due_date).days if factory_bid.expect_work_day and req_order.due_date else 0,
                })
            else:
                # 입찰 정보가 없을 때 기본값 설정
                order_data.update({
                    'unitPrice': 0,
                    'totalPrice': 0,
                })
            
            orders_data.append(order_data)
        
        return Response({'results': orders_data}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception('get_factory_orders error')
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_designer_orders(request):
    """
    디자이너용 주문 목록 조회
    """
    try:
        # 디자이너 권한 확인
        if not hasattr(request.user, 'designer'):
            return Response({'detail': '디자이너만 접근할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        # 해당 디자이너의 주문들 조회
        orders = Order.objects.filter(
            product__designer=request.user.designer
        ).select_related('product').prefetch_related('request_orders')
        
        orders_data = []
        for order in orders:
            # RequestOrder 정보 가져오기
            request_order = order.request_orders.first()
            
            order_data = {
                'id': order.order_id,
                'order_id': order.order_id,
                'status': 'pending',  # 기본값
                'created_at': order.product.created_at,
                'quantity': request_order.quantity if request_order else order.product.quantity,
                'product': {
                    'id': order.product.id,
                    'name': order.product.name,
                    'designer': order.product.designer.id,
                },
                'productInfo': {
                    'id': order.product.id,
                    'name': order.product.name,
                    'designer': order.product.designer.id,
                    'designerName': order.product.designer.name,
                }
            }
            
            orders_data.append(order_data)
        
        return Response({'results': orders_data}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.exception('get_designer_orders error')
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_factory_bid(request):
    """
    공장 입찰 생성
    """
    try:
        # 공장주 권한 확인
        if not hasattr(request.user, 'factory'):
            return Response({'detail': '공장주만 입찰할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data.copy()
        data['factory'] = request.user.factory.id
        
        # RequestOrder ID를 통해 RequestOrder 객체 가져오기
        request_order_id = data.get('order')  # 프론트에서 order로 전송
        if not request_order_id:
            return Response({'detail': 'order 필드가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            request_order = RequestOrder.objects.get(id=request_order_id)
            data['request_order'] = request_order.id
        except RequestOrder.DoesNotExist:
            return Response({'detail': '해당 주문을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        
        # 예상 납기일 계산 (단가와 예상 작업일수로부터)
        estimated_delivery_days = data.get('estimated_delivery_days', 7)
        from datetime import datetime, timedelta
        data['expect_work_day'] = (datetime.now().date() + timedelta(days=estimated_delivery_days))
        data['work_price'] = data.get('unit_price')
        
        serializer = BidFactoryCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.exception('create_factory_bid error')
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)