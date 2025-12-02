import os
import pickle
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, time
import numpy as np
from django.conf import settings
from django.utils import timezone
from apps.fields.models import Field
from weather_integration.services import WeatherService, OpenWeatherMapService
from .models import IrrigationSchedule

logger = logging.getLogger(__name__)


# Zambian Province Center Coordinates (approximate centers for each province)
ZAMBIA_REGION_COORDINATES = {
    'lusaka': {'lat': -15.3875, 'lon': 28.3228, 'city': 'Lusaka'},
    'central': {'lat': -14.4667, 'lon': 28.9500, 'city': 'Kabwe'},
    'southern': {'lat': -17.8500, 'lon': 25.8500, 'city': 'Livingstone'},
    'eastern': {'lat': -13.6333, 'lon': 32.6500, 'city': 'Chipata'},
    'copperbelt': {'lat': -12.8167, 'lon': 28.2167, 'city': 'Ndola'},
    'northern': {'lat': -10.2167, 'lon': 31.1333, 'city': 'Kasama'},
    'western': {'lat': -15.0833, 'lon': 23.1333, 'city': 'Mongu'},
    'luapula': {'lat': -10.7167, 'lon': 28.8833, 'city': 'Mansa'},
    'muchinga': {'lat': -10.4333, 'lon': 32.0833, 'city': 'Chinsali'},
    'northwestern': {'lat': -12.3667, 'lon': 25.8167, 'city': 'Solwezi'},
}


class IrrigationPredictionService:
    """
    Service for loading and using the Random Forest model to predict irrigation needs.
    """

    MODEL_PATH = os.path.join(settings.BASE_DIR, '..', 'rf_irrigation_model.pkl')

    # Model feature names (must match training data)
    FEATURE_NAMES = [
        'CropType', 'CropDays', 'SoilMoisture', 'temperature',
        'humidity', 'rainfall', 'windspeed', 'soilType', 'region', 'season'
    ]

    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        """
        Load the trained Random Forest model from pickle file.
        """
        try:
            if not os.path.exists(self.MODEL_PATH):
                logger.error(f"Model file not found at {self.MODEL_PATH}")
                raise FileNotFoundError(f"Model file not found: {self.MODEL_PATH}")

            with open(self.MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)

            logger.info("Random Forest model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise

    def _encode_categorical_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encode categorical features to match model training format.
        """
        encoded_data = data.copy()

        # CropType encoding (based on Zambian crops)
        crop_mapping = {
            'Maize': 0, 'Wheat': 1, 'Rice': 2, 'Tomatoes': 3,
            'Potatoes': 4, 'Cotton': 5
        }
        encoded_data['CropType'] = crop_mapping.get(data['CropType'], 0)

        # soilType encoding
        soil_mapping = {
            'Clay': 0, 'Loam': 1, 'Sandy': 2, 'Silty': 3
        }
        encoded_data['soilType'] = soil_mapping.get(data['soilType'], 1)

        # region encoding (Zambian provinces)
        region_mapping = {
            'Lusaka': 0, 'Central Province': 1, 'Southern Province': 2,
            'Eastern Province': 3, 'Copperbelt': 4, 'Northern Province': 5,
            'Western Province': 6, 'Luapula': 7, 'Muchinga': 8, 'North-Western': 9
        }
        encoded_data['region'] = region_mapping.get(data['region'], 0)

        # season encoding
        season_mapping = {
            'Dry': 0, 'Wet': 1
        }
        encoded_data['season'] = season_mapping.get(data['season'], 0)

        return encoded_data

    # Removed hardcoded DEFAULT_LATITUDE/LONGITUDE - now using geocoding

    def _get_coordinates_for_field(self, field: Field) -> Tuple[float, float]:
        """
        Get coordinates for a field, using multiple fallback strategies:
        1. Use field's stored latitude/longitude if available
        2. Look up coordinates from region mapping
        3. Use geocoding API to fetch coordinates from region city name
        4. Default to Lusaka as last resort
        """
        # Strategy 1: Use field's stored coordinates
        if field.latitude and field.longitude:
            logger.info(f"Using field's stored coordinates: {field.latitude}, {field.longitude}")
            return float(field.latitude), float(field.longitude)
        
        # Strategy 2: Look up from region mapping
        region_key = field.region.lower() if field.region else None
        if region_key and region_key in ZAMBIA_REGION_COORDINATES:
            region_data = ZAMBIA_REGION_COORDINATES[region_key]
            logger.info(f"Using region coordinates for {field.region}: {region_data['lat']}, {region_data['lon']}")
            
            # Auto-update field coordinates for future use
            try:
                field.latitude = region_data['lat']
                field.longitude = region_data['lon']
                field.save(update_fields=['latitude', 'longitude'])
                logger.info(f"Auto-updated field {field.name} with coordinates from region {field.region}")
            except Exception as e:
                logger.warning(f"Could not auto-save coordinates to field: {e}")
            
            return region_data['lat'], region_data['lon']
        
        # Strategy 3: Use geocoding API
        try:
            weather_api = OpenWeatherMapService()
            city_name = None
            
            # Try to get city name from region
            if region_key and region_key in ZAMBIA_REGION_COORDINATES:
                city_name = ZAMBIA_REGION_COORDINATES[region_key]['city']
            elif field.region:
                # Use region name as city name
                city_name = field.region.replace('_', ' ').title()
            
            if city_name:
                coords = weather_api.get_coordinates_by_city(city_name, 'ZM')
                if coords:
                    logger.info(f"Geocoded {city_name}, ZM to: {coords['lat']}, {coords['lon']}")
                    
                    # Auto-update field coordinates
                    try:
                        field.latitude = coords['lat']
                        field.longitude = coords['lon']
                        field.save(update_fields=['latitude', 'longitude'])
                        logger.info(f"Auto-updated field {field.name} with geocoded coordinates")
                    except Exception as e:
                        logger.warning(f"Could not auto-save geocoded coordinates: {e}")
                    
                    return coords['lat'], coords['lon']
        except Exception as e:
            logger.warning(f"Geocoding failed: {e}")
        
        # Strategy 4: Default to Lusaka (capital of Zambia)
        logger.warning(f"Falling back to Lusaka coordinates for field {field.name}")
        return -15.3875, 28.3228

    def _get_weather_data(self, field: Field) -> Optional[Dict[str, Any]]:
        """
        Get current weather data for the field's location.
        Uses geocoding to determine coordinates from field region.
        """
        try:
            weather_service = WeatherService()
            
            # Get coordinates using geocoding strategy
            latitude, longitude = self._get_coordinates_for_field(field)
            
            logger.info(f"Fetching weather for field {field.name} at ({latitude}, {longitude})")
            
            weather_obj = weather_service.get_current_weather(
                latitude=latitude,
                longitude=longitude
            )

            if weather_obj:
                # Convert model instance to dict with numeric values
                weather_data = {
                    'temperature': float(weather_obj.temperature) if weather_obj.temperature else 25.0,
                    'humidity': float(weather_obj.humidity) if weather_obj.humidity else 60.0,
                    'rainfall': float(weather_obj.rainfall_1h) if weather_obj.rainfall_1h else 0.0,
                    'windspeed': float(weather_obj.wind_speed) if weather_obj.wind_speed else 5.0
                }
                logger.info(f"Got weather data for {field.name}: temp={weather_data['temperature']}°C, humidity={weather_data['humidity']}%")
                return weather_data
        except Exception as e:
            logger.warning(f"Failed to get weather data: {str(e)}")

        # Return default values if weather service fails
        logger.warning(f"Using default weather values for field {field.name}")
        return {
            'temperature': 25.0,
            'humidity': 60.0,
            'rainfall': 0.0,
            'windspeed': 5.0
        }

    def _prepare_model_input(self, field: Field) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Prepare input data for the model prediction.
        """
        # Get current weather data
        weather_data = self._get_weather_data(field)

        # Prepare raw input data
        raw_data = {
            'CropType': field.crop_type,
            'CropDays': field.crop_days,
            'SoilMoisture': field.current_soil_moisture,
            'temperature': weather_data['temperature'],
            'humidity': weather_data['humidity'],
            'rainfall': weather_data['rainfall'],
            'windspeed': weather_data['windspeed'],
            'soilType': field.soil_type,
            'region': field.get_region_display(),
            'season': field.current_season
        }

        # Encode categorical features
        encoded_data = self._encode_categorical_features(raw_data)

        # Create feature array in correct order
        features = np.array([[
            encoded_data[feature] for feature in self.FEATURE_NAMES
        ]])

        return features, raw_data

    def predict_irrigation_need(self, field: Field) -> Tuple[float, float, Dict[str, Any]]:
        """
        Predict irrigation water amount and confidence for a field.

        Returns:
            Tuple of (predicted_water_amount, confidence_score, input_data)
        """
        if not self.model:
            raise ValueError("Model not loaded")

        # Prepare input data
        features, raw_data = self._prepare_model_input(field)

        # Make prediction
        try:
            prediction = self.model.predict(features)[0]

            # Calculate confidence score (using prediction probability if available)
            if hasattr(self.model, 'predict_proba'):
                # For classification models, use probability of positive class
                proba = self.model.predict_proba(features)[0]
                confidence = float(max(proba)) if len(proba) > 1 else 0.5
            else:
                # For regression models, use a simple confidence metric
                # This is a placeholder - you might want to implement proper confidence intervals
                confidence = 0.8  # Default confidence

            # Ensure prediction is positive and reasonable
            predicted_amount = max(0, float(prediction))

            return predicted_amount, confidence, raw_data

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise

    def _determine_priority(self, predicted_amount: float, soil_moisture: float) -> str:
        """
        Determine irrigation priority based on prediction and soil moisture.
        """
        if soil_moisture < 20 or predicted_amount > 100:
            return 'critical'
        elif soil_moisture < 30 or predicted_amount > 50:
            return 'high'
        elif soil_moisture < 40 or predicted_amount > 25:
            return 'medium'
        else:
            return 'low'

    def _get_priority_description(self, priority: str) -> str:
        """
        Get a user-friendly description of the priority level.
        """
        descriptions = {
            'critical': 'Immediate irrigation needed - your crop is at risk of water stress',
            'high': 'Irrigation recommended within the next 24 hours',
            'medium': 'Schedule irrigation in the next 2-3 days',
            'low': 'No urgent irrigation needed - conditions are favorable'
        }
        return descriptions.get(priority, 'Schedule irrigation as convenient')

    def _get_water_amount_explanation(self, predicted_amount: float, field: Field) -> str:
        """
        Generate a user-friendly explanation of what the predicted water amount means.
        The model predicts liters per square meter (L/m²).
        We also calculate total water needed for the entire field.
        """
        # Calculate total water for the field (area is in hectares, 1 hectare = 10,000 m²)
        field_area_m2 = float(field.area) * 10000  # Convert hectares to m²
        total_liters = predicted_amount * field_area_m2
        total_m3 = total_liters / 1000  # Convert to cubic meters
        
        # Format the totals nicely
        if total_liters < 1000:
            total_display = f"{total_liters:.0f} liters"
        elif total_liters < 10000:
            total_display = f"{total_liters/1000:.1f} m³ ({total_liters:.0f} liters)"
        else:
            total_display = f"{total_m3:.1f} m³"
        
        if predicted_amount < 1:
            return f"Minimal watering needed ({predicted_amount:.1f} L/m²). Your {field.crop_type} crop has sufficient moisture. For your {field.area} hectare field, this means approximately {total_display} total."
        elif predicted_amount < 3:
            return f"Light irrigation recommended ({predicted_amount:.1f} L/m²) for your {field.crop_type} crop. For your {field.area} hectare field, apply approximately {total_display}."
        elif predicted_amount < 5:
            return f"Moderate irrigation needed ({predicted_amount:.1f} L/m²). Your {field.crop_type} will benefit from watering. For your {field.area} hectare field, apply approximately {total_display}."
        elif predicted_amount < 8:
            return f"Substantial irrigation required ({predicted_amount:.1f} L/m²). Your {field.crop_type} crop needs water. For your {field.area} hectare field, apply approximately {total_display}."
        else:
            return f"Heavy irrigation urgently needed ({predicted_amount:.1f} L/m²)! Your {field.crop_type} crop is water-stressed. For your {field.area} hectare field, apply approximately {total_display}."

    def _generate_irrigation_reason(self, field: Field, predicted_amount: float,
                                  soil_moisture: float, weather_data: Dict) -> str:
        """
        Generate human-readable explanation for the irrigation recommendation.
        """
        reasons = []

        # Soil moisture analysis
        if soil_moisture < 20:
            reasons.append(f"⚠️ Soil moisture is critically low at {soil_moisture}% - crops are water-stressed")
        elif soil_moisture < 30:
            reasons.append(f"🟡 Soil moisture is low at {soil_moisture}% - irrigation recommended soon")
        elif soil_moisture < 40:
            reasons.append(f"🔵 Soil moisture at {soil_moisture}% - approaching lower optimal range")
        else:
            reasons.append(f"✅ Soil moisture is adequate at {soil_moisture}%")

        # Temperature analysis
        temp = weather_data.get('temperature', 25)
        if temp > 35:
            reasons.append(f"🔥 Very high temperature ({temp:.1f}°C) causing rapid water loss")
        elif temp > 30:
            reasons.append(f"☀️ High temperature ({temp:.1f}°C) increases evaporation")
        elif temp < 15:
            reasons.append(f"❄️ Cool temperature ({temp:.1f}°C) reduces water needs")
        else:
            reasons.append(f"🌡️ Temperature is optimal ({temp:.1f}°C)")

        # Humidity analysis (air humidity from weather)
        humidity = weather_data.get('humidity', 60)
        if humidity < 30:
            reasons.append(f"💨 Very low air humidity ({humidity:.0f}%) accelerates water loss")
        elif humidity < 40:
            reasons.append(f"Low air humidity ({humidity:.0f}%) increases evaporation")
        elif humidity > 80:
            reasons.append(f"💧 High air humidity ({humidity:.0f}%) reduces irrigation needs")
        else:
            reasons.append(f"Air humidity is moderate ({humidity:.0f}%)")

        # Rainfall analysis
        rainfall = weather_data.get('rainfall', 0)
        if rainfall > 10:
            reasons.append(f"🌧️ Recent rainfall ({rainfall:.1f}mm) - may delay irrigation")
        elif rainfall > 0:
            reasons.append(f"Light rain detected ({rainfall:.1f}mm)")

        return " • ".join(reasons)

    def _get_weather_summary(self, weather_data: Dict) -> str:
        """
        Generate a human-readable weather summary.
        """
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 60)
        rainfall = weather_data.get('rainfall', 0)
        wind = weather_data.get('windspeed', 5)

        # Determine overall weather condition
        if rainfall > 5:
            condition = "Rainy"
        elif temp > 30 and humidity < 40:
            condition = "Hot & Dry"
        elif temp > 30:
            condition = "Hot"
        elif humidity > 70:
            condition = "Humid"
        elif temp < 18:
            condition = "Cool"
        else:
            condition = "Pleasant"

        return f"{condition} - {temp:.1f}°C, {humidity:.0f}% humidity"

    def _calculate_optimal_timing(self, field: Field) -> Tuple[datetime.date, time]:
        """
        Calculate optimal irrigation timing based on crop type and weather.
        """
        from datetime import timedelta

        # Default to tomorrow morning
        recommended_date = timezone.now().date() + timedelta(days=1)
        recommended_time = time(6, 0)  # 6:00 AM

        # Adjust based on crop type
        crop_timings = {
            'Rice': time(5, 0),  # Early morning for rice
            'Maize': time(6, 0),  # Standard morning
            'Cotton': time(7, 0),  # Later morning to avoid dew
        }

        if field.crop_type in crop_timings:
            recommended_time = crop_timings[field.crop_type]

        return recommended_date, recommended_time

    def generate_irrigation_schedule(self, field: Field, user) -> IrrigationSchedule:
        """
        Generate a complete irrigation schedule for a field using AI prediction.
        If a schedule already exists for the same field/date/time, update it instead.
        """
        # Get AI prediction
        predicted_amount, confidence, input_data = self.predict_irrigation_need(field)

        # Get weather data for reasoning
        weather_data = self._get_weather_data(field)

        # Determine priority and timing
        priority = self._determine_priority(predicted_amount, field.current_soil_moisture)
        recommended_date, recommended_time = self._calculate_optimal_timing(field)

        # Generate explanation
        reason = self._generate_irrigation_reason(
            field, predicted_amount, field.current_soil_moisture, weather_data
        )

        # Try to get existing schedule or create new one
        schedule, created = IrrigationSchedule.objects.update_or_create(
            field=field,
            recommended_date=recommended_date,
            recommended_time=recommended_time,
            defaults={
                'user': user,
                'predicted_water_amount': predicted_amount,
                'confidence_score': confidence,
                'irrigation_reason': reason,
                'priority_level': priority,
                'status': 'pending',  # Reset status when regenerating
                'model_input_data': input_data,
                'model_prediction_details': {
                    'predicted_amount': predicted_amount,
                    'confidence_score': confidence,
                    'weather_data': weather_data,
                    'model_features': self.FEATURE_NAMES
                }
            }
        )

        action = "Created" if created else "Updated"
        logger.info(f"{action} irrigation schedule for field {field.name}: {predicted_amount}L")
        return schedule

    def get_prediction_for_field(self, field: Field) -> Dict[str, Any]:
        """
        Get prediction data for a field without creating a schedule.
        Returns comprehensive, user-friendly prediction information.
        
        Note: The model predicts water amount in Liters per square meter (L/m²).
        We calculate total water needed based on field size.
        """
        predicted_amount, confidence, input_data = self.predict_irrigation_need(field)
        weather_data = self._get_weather_data(field)
        priority = self._determine_priority(predicted_amount, field.current_soil_moisture)
        
        # Calculate total water for the entire field
        field_area_m2 = float(field.area) * 10000  # hectares to m²
        total_water_liters = round(predicted_amount * field_area_m2, 0)
        total_water_m3 = round(total_water_liters / 1000, 1)

        return {
            # Core prediction data
            'predicted_water_amount': round(predicted_amount, 2),  # L/m²
            'predicted_water_unit': 'L/m²',
            'total_water_liters': total_water_liters,
            'total_water_m3': total_water_m3,
            'confidence_score': confidence,
            'priority': priority,
            
            # User-friendly descriptions
            'priority_description': self._get_priority_description(priority),
            'water_amount_explanation': self._get_water_amount_explanation(predicted_amount, field),
            'reason': self._generate_irrigation_reason(
                field, predicted_amount, field.current_soil_moisture, weather_data
            ),
            
            # Weather information
            'weather_data': {
                'temperature': round(weather_data['temperature'], 1),
                'humidity': round(weather_data['humidity'], 0),
                'rainfall': round(weather_data['rainfall'], 1),
                'windspeed': round(weather_data['windspeed'], 1)
            },
            'weather_summary': self._get_weather_summary(weather_data),
            
            # Field context
            'field_info': {
                'crop_type': field.crop_type,
                'crop_days': field.crop_days,
                'soil_moisture': field.current_soil_moisture,
                'soil_type': field.soil_type,
                'region': field.get_region_display(),
                'season': field.current_season,
                'area_hectares': float(field.area),
                'area_m2': field_area_m2
            },
            
            # Raw input data (for technical users)
            'input_data': input_data
        }