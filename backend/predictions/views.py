from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.fields.models import Field
from .models import IrrigationSchedule, IrrigationHistory
from .serializers import (
    IrrigationScheduleSerializer,
    IrrigationScheduleCreateSerializer,
    IrrigationScheduleUpdateSerializer,
    IrrigationHistorySerializer,
    IrrigationHistoryCreateSerializer
)
from .services import IrrigationPredictionService


class IrrigationScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing irrigation schedules.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = IrrigationScheduleSerializer

    def get_queryset(self):
        return IrrigationSchedule.objects.filter(user=self.request.user)\
            .select_related('field', 'user')\
            .order_by('-recommended_date', '-recommended_time')

    def get_serializer_class(self):
        if self.action == 'create':
            return IrrigationScheduleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return IrrigationScheduleUpdateSerializer
        return IrrigationScheduleSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate AI-powered irrigation schedule for a field.
        """
        field_id = request.data.get('field_id')
        if not field_id:
            return Response(
                {'error': 'field_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            field = get_object_or_404(Field, id=field_id, user=request.user)
        except Field.DoesNotExist:
            return Response(
                {'error': 'Field not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            service = IrrigationPredictionService()
            schedule = service.generate_irrigation_schedule(field, request.user)

            serializer = self.get_serializer(schedule)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Failed to generate schedule: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm an irrigation schedule (mark as confirmed).
        """
        schedule = self.get_object()
        if schedule.status != 'pending':
            return Response(
                {'error': 'Only pending schedules can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        schedule.status = 'confirmed'
        schedule.save()

        serializer = self.get_serializer(schedule)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def skip(self, request, pk=None):
        """
        Skip an irrigation schedule.
        """
        schedule = self.get_object()
        if schedule.status not in ['pending', 'confirmed']:
            return Response(
                {'error': 'Only pending or confirmed schedules can be skipped'},
                status=status.HTTP_400_BAD_REQUEST
            )

        schedule.status = 'skipped'
        schedule.save()

        serializer = self.get_serializer(schedule)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Get all pending irrigation schedules for the user.
        """
        queryset = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get all overdue irrigation schedules for the user.
        """
        queryset = self.get_queryset().filter(status__in=['pending', 'confirmed'])
        overdue_schedules = [s for s in queryset if s.is_overdue]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class IrrigationHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing irrigation history records.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = IrrigationHistorySerializer

    def get_queryset(self):
        return IrrigationHistory.objects.filter(user=self.request.user)\
            .select_related('field', 'user', 'related_schedule')\
            .order_by('-irrigation_date', '-irrigation_time')

    def get_serializer_class(self):
        if self.action == 'create':
            return IrrigationHistoryCreateSerializer
        return IrrigationHistorySerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def by_field(self, request):
        """
        Get irrigation history for a specific field.
        """
        field_id = request.query_params.get('field_id')
        if not field_id:
            return Response(
                {'error': 'field_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            field = get_object_or_404(Field, id=field_id, user=request.user)
        except Field.DoesNotExist:
            return Response(
                {'error': 'Field not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        queryset = self.get_queryset().filter(field=field)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent irrigation history (last 30 days).
        """
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        queryset = self.get_queryset().filter(
            irrigation_date__gte=thirty_days_ago.date()
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PredictionViewSet(viewsets.ViewSet):
    """
    ViewSet for AI prediction operations.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def predict(self, request):
        """
        Get AI prediction for a field without creating a schedule.
        """
        field_id = request.data.get('field_id')
        if not field_id:
            return Response(
                {'error': 'field_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            field = get_object_or_404(Field, id=field_id, user=request.user)
        except Field.DoesNotExist:
            return Response(
                {'error': 'Field not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            service = IrrigationPredictionService()
            prediction_data = service.get_prediction_for_field(field)

            return Response(prediction_data)

        except Exception as e:
            return Response(
                {'error': f'Prediction failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def field_predictions(self, request):
        """
        Get predictions for all user's fields.
        """
        try:
            service = IrrigationPredictionService()
            fields = Field.objects.filter(user=request.user)
            predictions = []

            for field in fields:
                try:
                    prediction_data = service.get_prediction_for_field(field)
                    prediction_data['field_id'] = field.id
                    prediction_data['field_name'] = field.name
                    predictions.append(prediction_data)
                except Exception as e:
                    predictions.append({
                        'field_id': field.id,
                        'field_name': field.name,
                        'error': str(e)
                    })

            return Response(predictions)

        except Exception as e:
            return Response(
                {'error': f'Failed to get predictions: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
