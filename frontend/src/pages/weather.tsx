import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AuthGuard from '@/components/auth/AuthGuard';
import Navigation from '@/components/Navigation';
import { weatherAPI } from '@/lib/api';
import {
  WeatherData,
  WeatherForecast,
  WeatherAlert,
  WeatherStats,
  getWeatherEmoji,
  formatTemperature
} from '@/types/weather';

export default function WeatherPage() {
  const { user } = useAuth();
  const [currentWeather, setCurrentWeather] = useState<WeatherData | null>(null);
  const [forecast, setForecast] = useState<WeatherForecast[]>([]);
  const [alerts, setAlerts] = useState<WeatherAlert[]>([]);
  const [stats, setStats] = useState<WeatherStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  // Default location (Lusaka, Zambia - can be made configurable later)
  const defaultLocation = {
    latitude: -15.3875,
    longitude: 28.3228,
    location_name: 'Lusaka, Zambia'
  };

  useEffect(() => {
    loadWeatherData();
  }, []);

  const loadWeatherData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load current weather
      const weatherData = await weatherAPI.getCurrent(defaultLocation);
      setCurrentWeather(weatherData);

      // Load forecast
      const forecastData = await weatherAPI.getForecast({ ...defaultLocation, days: 7 });
      setForecast(forecastData);

      // Load weather stats
      const statsData = await weatherAPI.getStats(defaultLocation.latitude, defaultLocation.longitude, 7);
      setStats(statsData);

      // Load alerts (if available)
      const alertsData = await weatherAPI.getAlerts(defaultLocation.latitude, defaultLocation.longitude);
      setAlerts(alertsData);

    } catch (err) {
      setError('Failed to load weather data. Please try again.');
      console.error('Weather data loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await weatherAPI.refresh(defaultLocation);
      await loadWeatherData();
    } catch (err) {
      console.error('Refresh error:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { weekday: 'short' });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <AuthGuard>
        <div className="min-h-screen bg-gray-50">
          <Navigation currentPage="weather" />
          <main className="max-w-7xl mx-auto px-4 py-8">
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading weather data...</p>
              </div>
            </div>
          </main>
        </div>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Navigation currentPage="weather" />

        <main className="max-w-7xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Weather Overview</h1>
              <p className="text-gray-600 mt-1">
                Current conditions and forecast for irrigation planning
              </p>
            </div>
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 flex items-center gap-2"
            >
              {refreshing ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                '🔄'
              )}
              Refresh
            </button>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Current Weather */}
          {currentWeather && (
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl shadow-lg p-8 mb-8">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-lg mb-2">Current Weather</p>
                  <p className="text-6xl font-bold mb-2">
                    {formatTemperature(currentWeather.temperature)}
                  </p>
                  <p className="text-xl mb-4">{currentWeather.weather_description}</p>
                  <div className="grid grid-cols-2 gap-4 text-blue-100">
                    <div>
                      <p className="text-sm">Feels like</p>
                      <p className="font-semibold">{formatTemperature(currentWeather.feels_like)}</p>
                    </div>
                    <div>
                      <p className="text-sm">Humidity</p>
                      <p className="font-semibold">{currentWeather.humidity}%</p>
                    </div>
                    <div>
                      <p className="text-sm">Wind</p>
                      <p className="font-semibold">
                        {currentWeather.wind_speed} m/s {currentWeather.wind_direction_cardinal}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm">Pressure</p>
                      <p className="font-semibold">{currentWeather.pressure} hPa</p>
                    </div>
                  </div>
                </div>
                <div className="text-8xl">
                  {getWeatherEmoji(currentWeather.weather_icon)}
                </div>
              </div>
            </div>
          )}

          {/* Weather Stats */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Temperature Range</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Min:</span>
                    <span className="font-semibold">{Math.round(stats.temperature.min)}°C</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Max:</span>
                    <span className="font-semibold">{Math.round(stats.temperature.max)}°C</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Average:</span>
                    <span className="font-semibold">{Math.round(stats.temperature.avg)}°C</span>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Humidity & Rain</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Humidity:</span>
                    <span className="font-semibold">{Math.round(stats.humidity.avg)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Max Rain Chance:</span>
                    <span className="font-semibold">{Math.round(stats.precipitation.max_probability)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Rainy Days:</span>
                    <span className="font-semibold">{stats.precipitation.days_with_rain}</span>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Irrigation Insights</h3>
                <div className="space-y-3">
                  {stats.precipitation.days_with_rain > 3 ? (
                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-blue-800 font-medium">💧 Natural Rain Expected</p>
                      <p className="text-blue-600 text-sm">Consider reducing irrigation schedule</p>
                    </div>
                  ) : stats.temperature.avg > 30 ? (
                    <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                      <p className="text-orange-800 font-medium">🔥 High Temperatures</p>
                      <p className="text-orange-600 text-sm">Increase irrigation frequency</p>
                    </div>
                  ) : (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <p className="text-green-800 font-medium">✅ Optimal Conditions</p>
                      <p className="text-green-600 text-sm">Standard irrigation schedule recommended</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* 7-Day Forecast */}
          {forecast.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">7-Day Forecast</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
                {forecast.slice(0, 7).map((day, index) => (
                  <div key={index} className="border rounded-lg p-4 text-center hover:bg-gray-50 transition-colors">
                    <p className="text-sm font-semibold text-gray-900 mb-3">
                      {formatDate(day.forecast_date)}
                    </p>
                    <div className="text-4xl mb-3">
                      {getWeatherEmoji(day.weather_icon)}
                    </div>
                    <p className="font-semibold text-gray-900 mb-1">
                      {formatTemperature(day.temperature_max)}
                    </p>
                    <p className="text-sm text-gray-500 mb-2">
                      {formatTemperature(day.temperature_min)}
                    </p>
                    <p className="text-xs text-gray-500">
                      {Math.round(parseFloat(day.precipitation_probability))}% rain
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Weather Alerts */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Weather Alerts</h2>
            {alerts.length > 0 ? (
              <div className="space-y-4">
                {alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className={`p-4 border-l-4 rounded-lg ${
                      alert.severity === 'extreme' ? 'border-red-500 bg-red-50' :
                      alert.severity === 'severe' ? 'border-orange-500 bg-orange-50' :
                      alert.severity === 'moderate' ? 'border-yellow-500 bg-yellow-50' :
                      'border-blue-500 bg-blue-50'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-semibold text-gray-900 mb-1">
                          {alert.title}
                        </p>
                        <p className="text-sm text-gray-700 mb-2">
                          {alert.description}
                        </p>
                        <p className="text-xs text-gray-600">
                          {formatDate(alert.start_time)} {formatTime(alert.start_time)} -
                          {formatDate(alert.end_time)} {formatTime(alert.end_time)}
                        </p>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        alert.severity === 'extreme' ? 'bg-red-100 text-red-800' :
                        alert.severity === 'severe' ? 'bg-orange-100 text-orange-800' :
                        alert.severity === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {alert.severity.toUpperCase()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">✅</div>
                <p className="text-gray-600">No active weather alerts</p>
                <p className="text-sm text-gray-500 mt-1">
                  Weather conditions are normal for irrigation activities
                </p>
              </div>
            )}
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}