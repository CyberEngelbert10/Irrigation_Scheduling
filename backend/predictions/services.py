import os
import pickle
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, time
import numpy as np
from django.conf import settings
from django.utils import timezone
from apps.fields.models import Field
from weather_integration.services import WeatherService
from .models import IrrigationSchedule

logger = logging.getLogger(__name__)


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

    def _get_weather_data(self, field: Field) -> Optional[Dict[str, Any]]:
        """
        Get current weather data for the field's location.
        """
        try:
            weather_service = WeatherService()
            weather_obj = weather_service.get_current_weather(
                latitude=field.latitude,
                longitude=field.longitude
            )

            if weather_obj:
                # Convert model instance to dict with numeric values
                return {
                    'temperature': float(weather_obj.temperature) if weather_obj.temperature else 25.0,
                    'humidity': float(weather_obj.humidity) if weather_obj.humidity else 60.0,
                    'rainfall': float(weather_obj.rainfall_1h) if weather_obj.rainfall_1h else 0.0,
                    'windspeed': float(weather_obj.wind_speed) if weather_obj.wind_speed else 5.0
                }
        except Exception as e:
            logger.warning(f"Failed to get weather data: {str(e)}")

        # Return default values if weather service fails
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

    def _generate_irrigation_reason(self, field: Field, predicted_amount: float,
                                  soil_moisture: float, weather_data: Dict) -> str:
        """
        Generate human-readable explanation for the irrigation recommendation.
        """
        reasons = []

        if soil_moisture < 30:
            reasons.append(f"Soil moisture is critically low at {soil_moisture}%")
        elif soil_moisture < 40:
            reasons.append(f"Soil moisture is low at {soil_moisture}%")

        if weather_data.get('temperature', 25) > 30:
            reasons.append(f"High temperature ({weather_data['temperature']}°C) increases water needs")

        if weather_data.get('humidity', 60) < 40:
            reasons.append(f"Low humidity ({weather_data['humidity']}%) increases evaporation")

        if predicted_amount > 50:
            reasons.append(f"AI model predicts high water requirement ({predicted_amount:.1f}L)")

        if not reasons:
            reasons.append("Regular maintenance irrigation recommended")

        return ". ".join(reasons)

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
        """
        predicted_amount, confidence, input_data = self.predict_irrigation_need(field)
        weather_data = self._get_weather_data(field)

        return {
            'predicted_water_amount': predicted_amount,
            'confidence_score': confidence,
            'input_data': input_data,
            'weather_data': weather_data,
            'priority': self._determine_priority(predicted_amount, field.current_soil_moisture),
            'reason': self._generate_irrigation_reason(
                field, predicted_amount, field.current_soil_moisture, weather_data
            )
        }