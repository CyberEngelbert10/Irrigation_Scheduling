from django.db.models import Sum, Avg, Count, F
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import timedelta

from predictions.models import IrrigationHistory


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def water_usage_stats(request):
    """
    Get comprehensive water usage statistics for the user.
    """
    try:
        user = request.user
        days = int(request.query_params.get('days', 30))

        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Base queryset
        history_queryset = IrrigationHistory.objects.filter(
            user=user,
            irrigation_date__gte=start_date.date()
        )

        # Total water usage
        total_usage = history_queryset.aggregate(
            total=Sum('water_amount_used')
        )['total'] or 0

        # Average daily usage
        daily_usage = history_queryset.values('irrigation_date').annotate(
            daily_total=Sum('water_amount_used')
        ).aggregate(avg_daily=Avg('daily_total'))['avg_daily'] or 0

        # Usage by field
        field_usage = history_queryset.values('field__name').annotate(
            total_usage=Sum('water_amount_used'),
            irrigation_count=Count('id')
        ).order_by('-total_usage')

        # Usage by method
        method_usage = history_queryset.values('irrigation_method').annotate(
            total_usage=Sum('water_amount_used'),
            count=Count('id')
        ).order_by('-total_usage')

        # Monthly trends (last 6 months)
        monthly_trends = IrrigationHistory.objects.filter(
            user=user,
            irrigation_date__gte=(end_date - timedelta(days=180)).date()
        ).annotate(
            month=TruncMonth('irrigation_date')
        ).values('month').annotate(
            total_usage=Sum('water_amount_used'),
            irrigation_count=Count('id')
        ).order_by('month')

        # Efficiency metrics
        rated_irrigation = history_queryset.exclude(effectiveness_rating__isnull=True)
        avg_rating = rated_irrigation.aggregate(
            avg_rating=Avg('effectiveness_rating')
        )['avg_rating']

        # Water savings potential (compared to average)
        avg_usage_per_minute = history_queryset.exclude(duration_minutes=0).aggregate(
            avg_per_minute=Avg(F('water_amount_used') / F('duration_minutes'))
        )['avg_per_minute'] or 0

        # Recent trends (last 7 days vs previous 7 days)
        week_ago = end_date - timedelta(days=7)
        two_weeks_ago = end_date - timedelta(days=14)

        recent_usage = IrrigationHistory.objects.filter(
            user=user,
            irrigation_date__gte=week_ago.date()
        ).aggregate(total=Sum('water_amount_used'))['total'] or 0

        previous_usage = IrrigationHistory.objects.filter(
            user=user,
            irrigation_date__gte=two_weeks_ago.date(),
            irrigation_date__lt=week_ago.date()
        ).aggregate(total=Sum('water_amount_used'))['total'] or 0

        usage_trend = None
        if previous_usage > 0:
            usage_trend = ((recent_usage - previous_usage) / previous_usage) * 100

        return Response({
            'period_days': days,
            'total_water_usage': float(total_usage),
            'average_daily_usage': float(daily_usage),
            'usage_by_field': list(field_usage),
            'usage_by_method': list(method_usage),
            'monthly_trends': list(monthly_trends),
            'efficiency_metrics': {
                'average_rating': float(avg_rating) if avg_rating else None,
                'rated_irrigation_count': rated_irrigation.count(),
                'total_irrigation_count': history_queryset.count(),
            },
            'water_efficiency': {
                'avg_liters_per_minute': float(avg_usage_per_minute),
            },
            'usage_trend': {
                'recent_week_liters': float(recent_usage),
                'previous_week_liters': float(previous_usage),
                'percentage_change': float(usage_trend) if usage_trend is not None else None,
            }
        })

    except Exception as e:
        return Response(
            {'error': f'Failed to calculate statistics: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def field_analytics(request, field_id):
    """
    Get detailed analytics for a specific field.
    """
    try:
        user = request.user
        days = int(request.query_params.get('days', 90))

        # Verify field ownership
        from apps.fields.models import Field
        field = Field.objects.get(id=field_id, user=user)

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Field-specific history
        history_queryset = IrrigationHistory.objects.filter(
            user=user,
            field=field,
            irrigation_date__gte=start_date.date()
        )

        # Basic stats
        total_usage = history_queryset.aggregate(
            total=Sum('water_amount_used')
        )['total'] or 0

        irrigation_count = history_queryset.count()

        # Soil moisture trends
        moisture_trends = history_queryset.exclude(
            soil_moisture_before__isnull=True,
            soil_moisture_after__isnull=True
        ).values('irrigation_date').annotate(
            avg_before=Avg('soil_moisture_before'),
            avg_after=Avg('soil_moisture_after'),
            count=Count('id')
        ).order_by('irrigation_date')

        # Effectiveness ratings over time
        rating_trends = history_queryset.exclude(
            effectiveness_rating__isnull=True
        ).values('irrigation_date').annotate(
            avg_rating=Avg('effectiveness_rating'),
            count=Count('id')
        ).order_by('irrigation_date')

        # Weekly usage patterns
        weekly_usage = history_queryset.annotate(
            week=TruncWeek('irrigation_date')
        ).values('week').annotate(
            total_usage=Sum('water_amount_used'),
            irrigation_count=Count('id')
        ).order_by('week')

        return Response({
            'field_id': field_id,
            'field_name': field.name,
            'period_days': days,
            'total_water_usage': float(total_usage),
            'irrigation_count': irrigation_count,
            'avg_usage_per_irrigation': float(total_usage) / irrigation_count if irrigation_count > 0 else 0,
            'soil_moisture_trends': list(moisture_trends),
            'effectiveness_trends': list(rating_trends),
            'weekly_usage': list(weekly_usage),
        })

    except Field.DoesNotExist:
        return Response(
            {'error': 'Field not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to get field analytics: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def irrigation_efficiency_report(request):
    """
    Generate a comprehensive irrigation efficiency report.
    """
    try:
        user = request.user
        days = int(request.query_params.get('days', 30))

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        history_queryset = IrrigationHistory.objects.filter(
            user=user,
            irrigation_date__gte=start_date.date()
        )

        # Efficiency analysis
        efficiency_data = history_queryset.values(
            'irrigation_method', 'effectiveness_rating'
        ).annotate(
            count=Count('id'),
            avg_rating=Avg('effectiveness_rating'),
            total_usage=Sum('water_amount_used'),
            avg_duration=Avg('duration_minutes')
        ).order_by('irrigation_method')

        # Best performing methods
        best_methods = sorted(
            [item for item in efficiency_data if item['avg_rating']],
            key=lambda x: x['avg_rating'],
            reverse=True
        )[:3]

        # Water waste indicators (high usage with low effectiveness)
        potential_waste = history_queryset.filter(
            effectiveness_rating__lte=2,
            water_amount_used__gt=history_queryset.aggregate(avg=Avg('water_amount_used'))['avg'] or 0
        ).values('id', 'irrigation_date', 'water_amount_used', 'effectiveness_rating')

        # Recommendations
        recommendations = []

        if efficiency_data:
            # Method recommendations
            drip_data = next((item for item in efficiency_data if item['irrigation_method'] == 'drip'), None)
            sprinkler_data = next((item for item in efficiency_data if item['irrigation_method'] == 'sprinkler'), None)

            if drip_data and sprinkler_data and drip_data['avg_rating'] and sprinkler_data['avg_rating']:
                if drip_data['avg_rating'] > sprinkler_data['avg_rating'] + 0.5:
                    recommendations.append({
                        'type': 'method_preference',
                        'title': 'Consider Drip Irrigation',
                        'description': f'Drip irrigation shows {drip_data["avg_rating"]:.1f} average rating vs {sprinkler_data["avg_rating"]:.1f} for sprinkler',
                        'priority': 'medium'
                    })

        # Duration optimization
        avg_duration = history_queryset.aggregate(avg=Avg('duration_minutes'))['avg']
        if avg_duration and avg_duration > 60:
            recommendations.append({
                'type': 'duration_optimization',
                'title': 'Review Irrigation Duration',
                'description': f'Average irrigation duration is {avg_duration:.0f} minutes. Consider shorter, more frequent sessions.',
                'priority': 'low'
            })

        return Response({
            'period_days': days,
            'efficiency_analysis': list(efficiency_data),
            'best_performing_methods': best_methods,
            'potential_water_waste': list(potential_waste),
            'recommendations': recommendations,
            'summary': {
                'total_irrigation_events': history_queryset.count(),
                'avg_effectiveness_rating': history_queryset.exclude(
                    effectiveness_rating__isnull=True
                ).aggregate(avg=Avg('effectiveness_rating'))['avg'],
                'most_used_method': max(efficiency_data, key=lambda x: x['count'])['irrigation_method'] if efficiency_data else None,
            }
        })

    except Exception as e:
        return Response(
            {'error': f'Failed to generate efficiency report: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
