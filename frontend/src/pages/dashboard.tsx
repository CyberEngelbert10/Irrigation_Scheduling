import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AuthGuard from '@/components/auth/AuthGuard';
import Navigation from '@/components/Navigation';
import { weatherAPI } from '@/lib/api';
import { WeatherData, getWeatherEmoji, formatTemperature } from '@/types/weather';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [currentWeather, setCurrentWeather] = useState<WeatherData | null>(null);
  const [weatherLoading, setWeatherLoading] = useState(true);

  // Default location (Lusaka, Zambia)
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
      setWeatherLoading(true);
      const weatherData = await weatherAPI.getCurrent(defaultLocation);
      setCurrentWeather(weatherData);
    } catch (err) {
      console.error('Failed to load weather data:', err);
    } finally {
      setWeatherLoading(false);
    }
  };

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Navigation currentPage="dashboard" />

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 py-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome back, {user?.name?.split(' ')[0]}! 👋
            </h2>
            <p className="text-gray-600">Here's your irrigation overview for today</p>
          </div>

          {/* Hero Card - Next Watering */}
          <div className="card bg-gradient-to-br from-primary-500 to-primary-600 text-white mb-8">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-primary-100 text-sm mb-2">NEXT WATERING SCHEDULED</p>
                <h3 className="text-3xl font-bold mb-3">Tomorrow Morning</h3>
                <p className="text-primary-50 mb-6">Optimal time: 6:00 AM - 8:00 AM</p>
                <button className="bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-primary-50 transition-colors">
                  View Schedule Details
                </button>
              </div>
              <div className="text-6xl">💧</div>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Weather Card */}
            <div className="card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => window.location.href = '/weather'}>
              {weatherLoading ? (
                <div className="flex items-center justify-center h-24">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                </div>
              ) : currentWeather ? (
                <>
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p className="text-gray-600 text-sm mb-1">CURRENT WEATHER</p>
                      <h3 className="text-2xl font-bold text-gray-900">
                        {formatTemperature(currentWeather.temperature)}
                      </h3>
                    </div>
                    <div className="text-4xl">{getWeatherEmoji(currentWeather.weather_icon)}</div>
                  </div>
                  <p className="text-gray-600 text-sm capitalize">{currentWeather.weather_description}</p>
                  <p className="text-gray-500 text-xs mt-1">
                    Humidity: {currentWeather.humidity}% • Wind: {currentWeather.wind_speed} m/s
                  </p>
                  <p className="text-primary-600 text-sm font-medium mt-2 hover:text-primary-700">
                    View detailed forecast →
                  </p>
                </>
              ) : (
                <>
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p className="text-gray-600 text-sm mb-1">CURRENT WEATHER</p>
                      <h3 className="text-2xl font-bold text-gray-900">--°C</h3>
                    </div>
                    <div className="text-4xl">🌤️</div>
                  </div>
                  <p className="text-gray-600 text-sm">Unable to load weather</p>
                  <p className="text-primary-600 text-sm font-medium mt-2 hover:text-primary-700">
                    View detailed forecast →
                  </p>
                </>
              )}
            </div>

            {/* Fields Card */}
            <div className="card">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="text-gray-600 text-sm mb-1">ACTIVE FIELDS</p>
                  <h3 className="text-2xl font-bold text-gray-900">0</h3>
                </div>
                <div className="text-4xl">🌾</div>
              </div>
              <p className="text-gray-600 text-sm mb-2">No fields added yet</p>
              <button className="text-primary-600 text-sm font-medium hover:text-primary-700">
                + Add Your First Field
              </button>
            </div>

            {/* Savings Card */}
            <div className="card">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <p className="text-gray-600 text-sm mb-1">WATER SAVED</p>
                  <h3 className="text-2xl font-bold text-gray-900">0L</h3>
                </div>
                <div className="text-4xl">💰</div>
              </div>
              <p className="text-gray-600 text-sm">This month</p>
              <p className="text-green-600 text-sm font-medium mt-2">Start saving water today!</p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button className="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all text-left">
                <div className="text-2xl mb-2">🌾</div>
                <h4 className="font-semibold text-gray-900 mb-1">Add New Field</h4>
                <p className="text-sm text-gray-600">Register a new field for irrigation scheduling</p>
              </button>
              <button className="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all text-left">
                <div className="text-2xl mb-2">📊</div>
                <h4 className="font-semibold text-gray-900 mb-1">View Analytics</h4>
                <p className="text-sm text-gray-600">Track your water usage and savings</p>
              </button>
            </div>
          </div>

          {/* Coming Soon Notice */}
          <div className="mt-8 p-6 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">🚀 Phase 1 Complete: Authentication</h3>
            <p className="text-blue-700 text-sm">
              You can now register, login, and manage your profile. Field management, weather integration, 
              and AI-powered scheduling coming in the next phases!
            </p>
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
