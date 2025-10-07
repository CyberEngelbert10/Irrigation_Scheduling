from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Field
from .serializers import (
    FieldSerializer,
    FieldCreateSerializer,
    FieldUpdateSerializer,
    FieldListSerializer,
    SoilMoistureUpdateSerializer,
)


class FieldViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Field CRUD operations.
    
    Endpoints:
    - GET /api/fields/ - List user's fields
    - POST /api/fields/ - Create new field
    - GET /api/fields/{id}/ - Get field details
    - PUT /api/fields/{id}/ - Full update field
    - PATCH /api/fields/{id}/ - Partial update field
    - DELETE /api/fields/{id}/ - Delete field
    - PATCH /api/fields/{id}/update_moisture/ - Update soil moisture only
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return only fields belonging to the authenticated user.
        Supports filtering by active status, crop type, and region.
        """
        queryset = Field.objects.filter(user=self.request.user).select_related('user')
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Filter by crop type
        crop_type = self.request.query_params.get('crop_type', None)
        if crop_type:
            queryset = queryset.filter(crop_type=crop_type)
        
        # Filter by region
        region = self.request.query_params.get('region', None)
        if region:
            queryset = queryset.filter(region=region)
        
        # Search by name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(location__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.
        """
        if self.action == 'list':
            return FieldListSerializer
        elif self.action == 'create':
            return FieldCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FieldUpdateSerializer
        elif self.action == 'update_moisture':
            return SoilMoistureUpdateSerializer
        return FieldSerializer
    
    def perform_create(self, serializer):
        """
        Save the field with the authenticated user.
        """
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new field and return full details.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full field details using FieldSerializer
        instance = serializer.instance
        output_serializer = FieldSerializer(instance)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a field (only if owned by user).
        """
        instance = self.get_object()
        
        # Double check ownership (queryset already filters, but extra security)
        if instance.user != request.user:
            return Response(
                {'detail': 'You do not have permission to delete this field.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        self.perform_destroy(instance)
        return Response(
            {'detail': 'Field deleted successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['patch'], url_path='update-moisture')
    def update_moisture(self, request, pk=None):
        """
        Update only the soil moisture for a field.
        
        PATCH /api/fields/{id}/update-moisture/
        Body: {"current_soil_moisture": 45}
        """
        field = self.get_object()
        
        serializer = self.get_serializer(field, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return full field data with updated moisture
        return Response(
            FieldSerializer(field).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'], url_path='ai-input')
    def get_ai_input(self, request, pk=None):
        """
        Get AI model input data for a field.
        Requires weather_data in query params or uses defaults.
        
        GET /api/fields/{id}/ai-input/?temperature=28&humidity=60&rainfall=0&windspeed=12
        """
        field = self.get_object()
        
        # Extract weather data from query params
        weather_data = {
            'temperature': float(request.query_params.get('temperature', 25)),
            'humidity': float(request.query_params.get('humidity', 60)),
            'rainfall': float(request.query_params.get('rainfall', 0)),
            'windspeed': float(request.query_params.get('windspeed', 10)),
        }
        
        # Get AI model input
        ai_input = field.get_ai_model_input(weather_data)
        
        return Response({
            'field_id': field.id,
            'field_name': field.name,
            'ai_model_input': ai_input,
            'weather_data_source': 'query_params',
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        Get user's field statistics.
        
        GET /api/fields/statistics/
        """
        queryset = self.get_queryset()
        
        total_fields = queryset.count()
        active_fields = queryset.filter(is_active=True).count()
        total_area = sum(float(field.area) for field in queryset)
        
        # Crop type distribution
        crop_distribution = {}
        for field in queryset:
            crop = field.get_crop_type_display()
            crop_distribution[crop] = crop_distribution.get(crop, 0) + 1
        
        # Region distribution
        region_distribution = {}
        for field in queryset:
            region = field.get_region_display()
            region_distribution[region] = region_distribution.get(region, 0) + 1
        
        return Response({
            'total_fields': total_fields,
            'active_fields': active_fields,
            'inactive_fields': total_fields - active_fields,
            'total_area_hectares': round(total_area, 2),
            'crop_distribution': crop_distribution,
            'region_distribution': region_distribution,
        }, status=status.HTTP_200_OK)
