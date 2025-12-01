import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AuthGuard from '@/components/auth/AuthGuard';
import Navigation from '@/components/Navigation';
import { weatherAPI, predictionsAPI, fieldAPI, analyticsAPI } from '@/lib/api';
import { WeatherData, getWeatherEmoji, formatTemperature } from '@/types/weather';
import { Field } from '@/types/field';
import { IrrigationSchedule, FieldPrediction, WaterUsageStats } from '@/types/predictions';
import { toast } from 'react-hot-toast';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [currentWeather, setCurrentWeather] = useState<WeatherData | null>(null);
  const [weatherLoading, setWeatherLoading] = useState(true);
  const [fields, setFields] = useState<Field[]>([]);
  const [fieldsLoading, setFieldsLoading] = useState(true);
  const [predictions, setPredictions] = useState<FieldPrediction[]>([]);
  const [predictionsLoading, setPredictionsLoading] = useState(true);
  const [pendingSchedules, setPendingSchedules] = useState<IrrigationSchedule[]>([]);
  const [schedulesLoading, setSchedulesLoading] = useState(true);
  const [analytics, setAnalytics] = useState<WaterUsageStats | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);
  const [generatingSchedules, setGeneratingSchedules] = useState(false);
  const [generatingForField, setGeneratingForField] = useState<number | null>(null);

  // Default location (Lusaka, Zambia)
  const defaultLocation = {
    latitude: -15.3875,
    longitude: 28.3228,
    location_name: 'Lusaka, Zambia'
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    await Promise.all([
      loadWeatherData(),
      loadFields(),
      loadPredictions(),
      loadPendingSchedules(),
      loadAnalytics()
    ]);
  };

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

  const loadFields = async () => {
    try {
      setFieldsLoading(true);
      const fieldsData = await fieldAPI.list({ is_active: true });
      setFields(fieldsData);
    } catch (err) {
      console.error('Failed to load fields:', err);
    } finally {
      setFieldsLoading(false);
    }
  };

  const loadPredictions = async () => {
    try {
      setPredictionsLoading(true);
      const predictionsData = await predictionsAPI.getFieldPredictions();
      setPredictions(predictionsData);
    } catch (err) {
      console.error('Failed to load predictions:', err);
    } finally {
      setPredictionsLoading(false);
    }
  };

  const loadPendingSchedules = async () => {
    try {
      setSchedulesLoading(true);
      const schedulesData = await predictionsAPI.getPendingSchedules();
      setPendingSchedules(schedulesData);
    } catch (err) {
      console.error('Failed to load schedules:', err);
    } finally {
      setSchedulesLoading(false);
    }
  };

  const loadAnalytics = async () => {
    try {
      setAnalyticsLoading(true);
      const analyticsData = await analyticsAPI.getWaterUsageStats({ days: 30 });
      setAnalytics(analyticsData);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setAnalyticsLoading(false);
    }
  };

  // Generate schedules for all fields with predictions
  const generateAllSchedules = async () => {
    if (predictions.length === 0) {
      toast.error('No predictions available to generate schedules');
      return;
    }

    setGeneratingSchedules(true);
    let successCount = 0;
    let errorCount = 0;

    try {
      for (const prediction of predictions) {
        try {
          await predictionsAPI.generateSchedule(prediction.field_id);
          successCount++;
        } catch (err) {
          console.error(`Failed to generate schedule for field ${prediction.field_name}:`, err);
          errorCount++;
        }
      }

      if (successCount > 0) {
        toast.success(`Generated ${successCount} irrigation schedule${successCount > 1 ? 's' : ''}`);
        // Reload schedules to show new ones
        await loadPendingSchedules();
        // Reload predictions (they might change after schedule generation)
        await loadPredictions();
      }

      if (errorCount > 0) {
        toast.error(`Failed to generate ${errorCount} schedule${errorCount > 1 ? 's' : ''}`);
      }
    } catch (err) {
      console.error('Failed to generate schedules:', err);
      toast.error('Failed to generate schedules');
    } finally {
      setGeneratingSchedules(false);
    }
  };

  // Generate schedule for a single field
  const generateScheduleForField = async (fieldId: number, fieldName: string) => {
    setGeneratingForField(fieldId);

    try {
      await predictionsAPI.generateSchedule(fieldId);
      toast.success(`Schedule generated for ${fieldName}`);
      // Reload schedules and predictions
      await Promise.all([loadPendingSchedules(), loadPredictions()]);
    } catch (err: any) {
      console.error(`Failed to generate schedule for ${fieldName}:`, err);
      toast.error(err.response?.data?.error || `Failed to generate schedule for ${fieldName}`);
    } finally {
      setGeneratingForField(null);
    }
  };

  // Confirm a pending schedule
  const confirmSchedule = async (scheduleId: number) => {
    try {
      await predictionsAPI.confirmSchedule(scheduleId);
      toast.success('Schedule confirmed');
      await loadPendingSchedules();
    } catch (err) {
      console.error('Failed to confirm schedule:', err);
      toast.error('Failed to confirm schedule');
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
                {pendingSchedules.length > 0 ? (
                  <>
                    <p className="text-primary-100 text-sm mb-2">NEXT IRRIGATION SCHEDULED</p>
                    <h3 className="text-3xl font-bold mb-3">
                      {new Date(pendingSchedules[0].recommended_date).toLocaleDateString('en-US', {
                        weekday: 'long',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </h3>
                    <p className="text-primary-50 mb-2">
                      {pendingSchedules[0].recommended_time.slice(0, 5)} • {pendingSchedules[0].field_name}
                    </p>
                    <p className="text-primary-50 mb-6">
                      {pendingSchedules[0].predicted_water_amount}L predicted • {Math.round(parseFloat(pendingSchedules[0].confidence_score) * 100)}% confidence
                    </p>
                    <div className="flex gap-3">
                      <button 
                        onClick={() => window.location.href = `/fields/${pendingSchedules[0].field}`}
                        className="bg-white text-primary-600 px-4 py-2 rounded-lg font-semibold hover:bg-primary-50 transition-colors text-sm"
                      >
                        View Details
                      </button>
                      <button 
                        onClick={() => confirmSchedule(pendingSchedules[0].id)}
                        className="bg-primary-400 text-white px-4 py-2 rounded-lg font-semibold hover:bg-primary-300 transition-colors text-sm"
                      >
                        Confirm Schedule
                      </button>
                    </div>
                  </>
                ) : predictions.length > 0 ? (
                  <>
                    <p className="text-primary-100 text-sm mb-2">AI IRRIGATION RECOMMENDATION</p>
                    <h3 className="text-3xl font-bold mb-3">Ready to Schedule</h3>
                    <p className="text-primary-50 mb-2">
                      {predictions.length} field{predictions.length > 1 ? 's' : ''} with AI recommendations
                    </p>
                    <p className="text-primary-50 mb-6">
                      Get personalized irrigation schedules based on weather and crop data
                    </p>
                    <button 
                      onClick={generateAllSchedules}
                      disabled={generatingSchedules}
                      className="bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-primary-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {generatingSchedules ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                          Generating...
                        </>
                      ) : (
                        'Generate Schedules'
                      )}
                    </button>
                  </>
                ) : (
                  <>
                    <p className="text-primary-100 text-sm mb-2">GET STARTED WITH AI</p>
                    <h3 className="text-3xl font-bold mb-3">Smart Irrigation</h3>
                    <p className="text-primary-50 mb-6">
                      Add fields and get AI-powered irrigation recommendations
                    </p>
                    <button 
                      onClick={() => window.location.href = '/fields/add'}
                      className="bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-primary-50 transition-colors"
                    >
                      Add Your First Field
                    </button>
                  </>
                )}
              </div>
              <div className="text-6xl">🤖</div>
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
                  <h3 className="text-2xl font-bold text-gray-900">
                    {fieldsLoading ? '...' : fields.length}
                  </h3>
                </div>
                <div className="text-4xl">🌾</div>
              </div>
              {fieldsLoading ? (
                <p className="text-gray-600 text-sm">Loading fields...</p>
              ) : fields.length > 0 ? (
                <>
                  <p className="text-gray-600 text-sm mb-2">
                    {fields.length} field{fields.length > 1 ? 's' : ''} ready for irrigation
                  </p>
                  <button
                    className="text-primary-600 text-sm font-medium hover:text-primary-700"
                    onClick={() => window.location.href = '/fields'}
                  >
                    Manage Fields →
                  </button>
                </>
              ) : (
                <>
                  <p className="text-gray-600 text-sm mb-2">No fields added yet</p>
                  <button
                    className="text-primary-600 text-sm font-medium hover:text-primary-700"
                    onClick={() => window.location.href = '/fields/add'}
                  >
                    + Add Your First Field
                  </button>
                </>
              )}
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

          {/* AI Recommendations Section */}
          {predictions.length > 0 && (
            <div className="card mb-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900">🤖 AI Irrigation Recommendations</h3>
                <span className="text-sm text-gray-500">
                  Updated {new Date().toLocaleTimeString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              </div>

              {predictionsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                  <span className="ml-3 text-gray-600">Analyzing your fields...</span>
                </div>
              ) : (
                <div className="space-y-4">
                  {predictions.map((prediction, index) => (
                    <div key={prediction.field_id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h4 className="font-semibold text-gray-900">{prediction.field_name}</h4>
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                              prediction.priority === 'critical' ? 'bg-red-100 text-red-800' :
                              prediction.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                              prediction.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {prediction.priority.toUpperCase()}
                            </span>
                          </div>

                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                            <div>
                              <p className="text-xs text-gray-500">Water Needed</p>
                              <p className="font-semibold text-gray-900">{prediction.predicted_water_amount.toFixed(1)}L</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Confidence</p>
                              <p className="font-semibold text-gray-900">{Math.round(prediction.confidence_score * 100)}%</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Temperature</p>
                              <p className="font-semibold text-gray-900">{prediction.weather_data.temperature}°C</p>
                            </div>
                            <div>
                              <p className="text-xs text-gray-500">Humidity</p>
                              <p className="font-semibold text-gray-900">{prediction.weather_data.humidity}%</p>
                            </div>
                          </div>

                          <p className="text-sm text-gray-600 mb-3">{prediction.reason}</p>

                          <div className="flex gap-2">
                            <button 
                              onClick={() => generateScheduleForField(prediction.field_id, prediction.field_name)}
                              disabled={generatingForField === prediction.field_id}
                              className="text-primary-600 text-sm font-medium hover:text-primary-700 disabled:opacity-50 flex items-center gap-1"
                            >
                              {generatingForField === prediction.field_id ? (
                                <>
                                  <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary-600"></div>
                                  Generating...
                                </>
                              ) : (
                                'Generate Schedule'
                              )}
                            </button>
                            <button 
                              onClick={() => window.location.href = `/fields/${prediction.field_id}`}
                              className="text-gray-500 text-sm hover:text-gray-700"
                            >
                              View Details
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Analytics Section */}
          <div className="card mb-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">📊 Water Usage Analytics</h3>
              <span className="text-sm text-gray-500">
                Last 30 days
              </span>
            </div>

            {analyticsLoading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                <span className="ml-3 text-gray-600">Analyzing your data...</span>
              </div>
            ) : analytics ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary-600 mb-1">
                    {analytics.total_water_usage.toFixed(1)}L
                  </div>
                  <p className="text-sm text-gray-600">Total Water Used</p>
                </div>

                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600 mb-1">
                    {analytics.average_daily_usage.toFixed(1)}L
                  </div>
                  <p className="text-sm text-gray-600">Daily Average</p>
                </div>

                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600 mb-1">
                    {analytics.efficiency_metrics.average_rating ?
                      `${analytics.efficiency_metrics.average_rating.toFixed(1)}⭐` :
                      'N/A'
                    }
                  </div>
                  <p className="text-sm text-gray-600">Avg Effectiveness</p>
                </div>

                <div className="text-center">
                  <div className={`text-2xl font-bold mb-1 ${
                    analytics.usage_trend.percentage_change && analytics.usage_trend.percentage_change > 0
                      ? 'text-red-600'
                      : analytics.usage_trend.percentage_change && analytics.usage_trend.percentage_change < 0
                      ? 'text-green-600'
                      : 'text-gray-600'
                  }`}>
                    {analytics.usage_trend.percentage_change ?
                      `${analytics.usage_trend.percentage_change > 0 ? '+' : ''}${analytics.usage_trend.percentage_change.toFixed(1)}%` :
                      'N/A'
                    }
                  </div>
                  <p className="text-sm text-gray-600">Weekly Trend</p>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No analytics data available yet. Start recording irrigation activities to see insights.</p>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button 
                onClick={() => window.location.href = '/fields/add'}
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all text-left"
              >
                <div className="text-2xl mb-2">🌾</div>
                <h4 className="font-semibold text-gray-900 mb-1">Add New Field</h4>
                <p className="text-sm text-gray-600">Register a new field for irrigation scheduling</p>
              </button>
              <button
                onClick={() => window.location.href = '/history'}
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all text-left"
              >
                <div className="text-2xl mb-2">�</div>
                <h4 className="font-semibold text-gray-900 mb-1">View History</h4>
                <p className="text-sm text-gray-600">Track your irrigation activities</p>
              </button>
            </div>
          </div>

          {/* Status Notice */}
          <div className="mt-8 p-6 bg-green-50 border border-green-200 rounded-lg">
            <h3 className="text-lg font-semibold text-green-900 mb-2">🎉 Phase 4 Complete: AI-Powered Irrigation</h3>
            <p className="text-green-700 text-sm">
              Your irrigation system now features AI-powered scheduling with weather integration!
              {fields.length === 0 ? ' Add your first field to get started with smart irrigation recommendations.' :
               predictions.length === 0 ? ' AI analysis is running for your fields.' :
               ` AI recommendations are ready for ${predictions.length} field${predictions.length > 1 ? 's' : ''}.`}
            </p>
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
