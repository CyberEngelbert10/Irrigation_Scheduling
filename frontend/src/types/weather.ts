export interface WeatherData {
  id: number;
  latitude: number;
  longitude: number;
  location_name?: string;
  temperature: string;
  feels_like: string;
  humidity: number;
  pressure: number;
  wind_speed: string;
  wind_direction: number;
  wind_direction_cardinal: string;
  weather_condition: string;
  weather_description: string;
  weather_icon: string;
  rainfall_1h: string;
  rainfall_3h: string;
  data_source: string;
  updated_at: string;
  is_stale: boolean;
}

export interface WeatherForecast {
  id: number;
  latitude: number;
  longitude: number;
  location_name?: string;
  forecast_date: string;
  forecast_time: string;
  temperature_min: string;
  temperature_max: string;
  humidity: number;
  pressure: number;
  wind_speed: string;
  wind_direction: number;
  weather_condition: string;
  weather_description: string;
  weather_icon: string;
  precipitation_probability: string;
  rainfall_amount: string;
  data_source: string;
  updated_at: string;
}

export interface WeatherAlert {
  id: number;
  latitude: number;
  longitude: number;
  location_name?: string;
  alert_type: string;
  severity: 'minor' | 'moderate' | 'severe' | 'extreme';
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  duration_hours: number;
  is_active: boolean;
  is_expired: boolean;
  data_source: string;
  updated_at: string;
}

export interface WeatherStats {
  temperature: {
    min: number;
    max: number;
    avg: number;
  };
  humidity: {
    min: number;
    max: number;
    avg: number;
  };
  precipitation: {
    max_probability: number;
    avg_probability: number;
    days_with_rain: number;
  };
  forecast_days: number;
  location?: string;
}

export interface WeatherDataRequest {
  latitude: number;
  longitude: number;
  location_name?: string;
}

export interface WeatherForecastRequest {
  latitude: number;
  longitude: number;
  days?: number;
}

// Weather icon mapping for display
export const WEATHER_ICONS: Record<string, string> = {
  '01d': '☀️', // clear sky day
  '01n': '🌙', // clear sky night
  '02d': '⛅', // few clouds day
  '02n': '☁️', // few clouds night
  '03d': '☁️', // scattered clouds
  '03n': '☁️',
  '04d': '☁️', // broken clouds
  '04n': '☁️',
  '09d': '🌦️', // shower rain
  '09n': '🌧️',
  '10d': '🌦️', // rain day
  '10n': '🌧️', // rain night
  '11d': '⛈️', // thunderstorm
  '11n': '⛈️',
  '13d': '❄️', // snow
  '13n': '❄️',
  '50d': '🌫️', // mist
  '50n': '🌫️',
};

// Helper function to get weather emoji
export function getWeatherEmoji(iconCode: string): string {
  return WEATHER_ICONS[iconCode] || '☀️';
}

// Helper function to format temperature
export function formatTemperature(temp: string | number): string {
  const tempNum = typeof temp === 'string' ? parseFloat(temp) : temp;
  return `${Math.round(tempNum)}°C`;
}

// Helper function to get severity color
export function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'extreme':
      return 'red';
    case 'severe':
      return 'orange';
    case 'moderate':
      return 'yellow';
    case 'minor':
      return 'blue';
    default:
      return 'gray';
  }
}