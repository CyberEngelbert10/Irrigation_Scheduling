import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AuthGuard from '@/components/auth/AuthGuard';
import Navigation from '@/components/Navigation';
import { weatherAPI, predictionsAPI, fieldAPI, analyticsAPI } from '@/lib/api';
import { WeatherData, formatTemperature } from '@/types/weather';
import { Field } from '@/types/field';
import { IrrigationSchedule, FieldPrediction, WaterUsageStats } from '@/types/predictions';
import { toast } from 'react-hot-toast';

// Icons as simple SVG components for better performance
const DropletIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
  </svg>
);

const ThermometerIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z" />
  </svg>
);

const ShieldCheckIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    <path d="M9 12l2 2 4-4" />
  </svg>
);

const CloudRainIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25" />
    <path d="M8 19v2M8 13v2M16 19v2M16 13v2M12 21v2M12 15v2" />
  </svg>
);

const ChevronDownIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 9l6 6 6-6" />
  </svg>
);

const MapPinIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
    <circle cx="12" cy="10" r="3" />
  </svg>
);

export default function Dashboard() {
  const { user } = useAuth();
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
              Welcome back, {user?.name?.split(' ')[0]}!
            </h2>
            <p className="text-lg text-gray-600">Here is your irrigation overview for today</p>
          </div>

          {/* Hero Card - Next Watering */}
          <div className="bg-white rounded-xl shadow-lg border-2 border-primary-200 mb-8 overflow-hidden">
            <div className="bg-primary-600 text-white px-6 py-4">
              <p className="text-lg font-medium">
                {pendingSchedules.length > 0 ? 'Next Scheduled Irrigation' :
                 predictions.length > 0 ? 'AI Recommendations Ready' :
                 'Get Started'}
              </p>
            </div>
            <div className="p-6">
              {pendingSchedules.length > 0 ? (
                <>
                  <h3 className="text-3xl font-bold text-gray-900 mb-3">
                    {new Date(pendingSchedules[0].recommended_date).toLocaleDateString('en-US', {
                      weekday: 'long',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </h3>
                  <div className="text-xl text-gray-700 mb-2">
                    <span className="font-medium">Time:</span> {pendingSchedules[0].recommended_time.slice(0, 5)}
                  </div>
                  <div className="text-xl text-gray-700 mb-2">
                    <span className="font-medium">Field:</span> {pendingSchedules[0].field_name}
                  </div>
                  <div className="text-xl text-gray-700 mb-6">
                    <span className="font-medium">Water amount:</span> {pendingSchedules[0].predicted_water_amount} L/m²
                  </div>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <button 
                      onClick={() => window.location.href = `/fields/${pendingSchedules[0].field}`}
                      className="py-3 px-6 bg-gray-200 text-gray-800 rounded-lg text-lg font-medium hover:bg-gray-300 transition-colors"
                    >
                      View Details
                    </button>
                    <button 
                      onClick={() => confirmSchedule(pendingSchedules[0].id)}
                      className="py-3 px-6 bg-green-600 text-white rounded-lg text-lg font-bold hover:bg-green-700 transition-colors"
                    >
                      Confirm This Schedule
                    </button>
                  </div>
                </>
              ) : predictions.length > 0 ? (
                <>
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">
                    {predictions.length} field{predictions.length > 1 ? 's' : ''} ready for irrigation planning
                  </h3>
                  <p className="text-lg text-gray-600 mb-6">
                    Our system has analyzed your fields based on current weather and soil conditions. 
                    Review the recommendations below and create irrigation schedules.
                  </p>
                  <button 
                    onClick={generateAllSchedules}
                    disabled={generatingSchedules}
                    className="w-full sm:w-auto py-4 px-8 bg-primary-600 text-white rounded-lg text-xl font-bold hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
                  >
                    {generatingSchedules ? (
                      <>
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                        Creating Schedules...
                      </>
                    ) : (
                      'Create All Schedules'
                    )}
                  </button>
                </>
              ) : (
                <>
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">Start Smart Irrigation</h3>
                  <p className="text-lg text-gray-600 mb-6">
                    Add your fields to get personalized irrigation recommendations based on weather, 
                    soil conditions, and crop needs.
                  </p>
                  <button 
                    onClick={() => window.location.href = '/fields/new'}
                    className="w-full sm:w-auto py-4 px-8 bg-primary-600 text-white rounded-lg text-xl font-bold hover:bg-primary-700 transition-colors"
                  >
                    Add Your First Field
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Weather Card */}
            <div className="bg-white rounded-xl shadow p-6 cursor-pointer hover:shadow-lg transition-shadow" onClick={() => window.location.href = '/weather'}>
              {weatherLoading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
              ) : currentWeather ? (
                <>
                  <p className="text-base font-medium text-gray-500 uppercase tracking-wide mb-3">Current Weather</p>
                  <h3 className="text-4xl font-bold text-gray-900 mb-2">
                    {formatTemperature(currentWeather.temperature)}
                  </h3>
                  <p className="text-lg text-gray-700 capitalize mb-1">{currentWeather.weather_description}</p>
                  <p className="text-base text-gray-600">
                    Humidity: {currentWeather.humidity}%
                  </p>
                  <p className="text-primary-600 text-base font-medium mt-4 hover:text-primary-700">
                    View full forecast
                  </p>
                </>
              ) : (
                <>
                  <p className="text-base font-medium text-gray-500 uppercase tracking-wide mb-3">Current Weather</p>
                  <h3 className="text-4xl font-bold text-gray-900 mb-2">--°C</h3>
                  <p className="text-lg text-gray-600">Unable to load weather</p>
                </>
              )}
            </div>

            {/* Fields Card */}
            <div className="bg-white rounded-xl shadow p-6">
              <p className="text-base font-medium text-gray-500 uppercase tracking-wide mb-3">Your Fields</p>
              <h3 className="text-4xl font-bold text-gray-900 mb-2">
                {fieldsLoading ? '...' : fields.length}
              </h3>
              {fieldsLoading ? (
                <p className="text-lg text-gray-600">Loading...</p>
              ) : fields.length > 0 ? (
                <>
                  <p className="text-lg text-gray-700 mb-4">
                    {fields.length} active field{fields.length > 1 ? 's' : ''}
                  </p>
                  <button
                    className="text-primary-600 text-base font-medium hover:text-primary-700"
                    onClick={() => window.location.href = '/fields'}
                  >
                    Manage Fields
                  </button>
                </>
              ) : (
                <>
                  <p className="text-lg text-gray-600 mb-4">No fields added yet</p>
                  <button
                    className="text-primary-600 text-base font-medium hover:text-primary-700"
                    onClick={() => window.location.href = '/fields/new'}
                  >
                    Add Your First Field
                  </button>
                </>
              )}
            </div>

            {/* Water Usage Card */}
            <div className="bg-white rounded-xl shadow p-6">
              <p className="text-base font-medium text-gray-500 uppercase tracking-wide mb-3">Water This Month</p>
              <h3 className="text-4xl font-bold text-gray-900 mb-2">
                {analyticsLoading ? '...' : 
                 analytics ? `${analytics.total_water_usage.toFixed(0)}L` : '0L'}
              </h3>
              <p className="text-lg text-gray-700 mb-2">Total used</p>
              {analytics && analytics.average_daily_usage > 0 && (
                <p className="text-base text-gray-600">
                  Average: {analytics.average_daily_usage.toFixed(0)}L per day
                </p>
              )}
            </div>
          </div>

          {/* AI Recommendations Section */}
          {predictions.length > 0 && (
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-bold text-gray-900">Irrigation Recommendations</h3>
                <span className="text-base text-gray-600">
                  Updated: {new Date().toLocaleTimeString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              </div>

              {predictionsLoading ? (
                <div className="flex items-center justify-center py-12 bg-white rounded-xl shadow">
                  <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600"></div>
                  <span className="ml-4 text-lg text-gray-600">Analyzing your fields...</span>
                </div>
              ) : (
                <div className="space-y-6">
                  {predictions.map((prediction) => {
                    const priorityConfig = {
                      critical: { 
                        bg: 'bg-red-50', 
                        border: 'border-red-200',
                        gradient: 'from-red-500 to-red-600',
                        badge: 'bg-red-100 text-red-800 border-red-200',
                        button: 'bg-red-600 hover:bg-red-700',
                        emoji: '🔴',
                        label: 'URGENT - Water Now'
                      },
                      high: { 
                        bg: 'bg-orange-50', 
                        border: 'border-orange-200',
                        gradient: 'from-orange-500 to-orange-600',
                        badge: 'bg-orange-100 text-orange-800 border-orange-200',
                        button: 'bg-orange-500 hover:bg-orange-600',
                        emoji: '🟠',
                        label: 'HIGH - Water Soon'
                      },
                      medium: { 
                        bg: 'bg-yellow-50', 
                        border: 'border-yellow-200',
                        gradient: 'from-yellow-500 to-yellow-600',
                        badge: 'bg-yellow-100 text-yellow-800 border-yellow-200',
                        button: 'bg-yellow-500 hover:bg-yellow-600',
                        emoji: '🟡',
                        label: 'MEDIUM - Schedule Water'
                      },
                      low: { 
                        bg: 'bg-green-50', 
                        border: 'border-green-200',
                        gradient: 'from-green-500 to-emerald-600',
                        badge: 'bg-green-100 text-green-800 border-green-200',
                        button: 'bg-green-600 hover:bg-green-700',
                        emoji: '🟢',
                        label: 'LOW - No Rush'
                      }
                    };
                    const config = priorityConfig[prediction.priority as keyof typeof priorityConfig] || priorityConfig.low;
                    
                    const totalWaterDisplay = prediction.total_water_liters 
                      ? prediction.total_water_liters >= 1000 
                        ? `${(prediction.total_water_liters/1000).toFixed(1)} m³`
                        : `${prediction.total_water_liters.toFixed(0)} L`
                      : null;

                    const tempDescription = prediction.weather_data.temperature > 30 ? 'Hot' :
                      prediction.weather_data.temperature > 25 ? 'Warm' :
                      prediction.weather_data.temperature > 18 ? 'Pleasant' : 'Cool';

                    const humidityDescription = prediction.weather_data.humidity > 80 ? 'Very humid' :
                      prediction.weather_data.humidity > 60 ? 'Humid' :
                      prediction.weather_data.humidity > 40 ? 'Moderate' : 'Dry';

                    return (
                      <div key={prediction.field_id}>
                        {/* Desktop Card - Clean Dashboard Design */}
                        <div className="hidden md:block border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                          {/* Header */}
                          <div className={`bg-gradient-to-r ${config.bg} px-6 py-4 border-b ${config.border}`}>
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <h2 className="text-xl font-bold text-gray-900">{prediction.field_name}</h2>
                                <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${config.badge} border`}>
                                  {config.emoji} {config.label}
                                </span>
                              </div>
                              <div className="text-sm text-gray-600">
                                Updated: {new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                              </div>
                            </div>
                          </div>

                          {/* Main Insight */}
                          <div className="px-6 py-5 bg-white">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">
                              {prediction.priority_description || `${prediction.field_name} needs attention`}
                            </h3>
                            {prediction.water_amount_explanation && (
                              <p className="text-gray-600">{prediction.water_amount_explanation}</p>
                            )}
                          </div>

                          {/* Metrics Grid */}
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 px-6 py-5 bg-gray-50">
                            {/* Water */}
                            <div className="bg-white p-4 rounded-lg border border-gray-200">
                              <div className="flex items-center gap-2 mb-2">
                                <DropletIcon className="w-4 h-4 text-blue-500" />
                                <span className="text-xs font-medium text-gray-600">Water Needed</span>
                              </div>
                              <div className="text-xl font-bold text-gray-900">{prediction.predicted_water_amount.toFixed(1)} L/m²</div>
                              {totalWaterDisplay && (
                                <div className="text-xs text-gray-500 mt-1">Total: {totalWaterDisplay}</div>
                              )}
                            </div>

                            {/* Confidence */}
                            <div className="bg-white p-4 rounded-lg border border-gray-200">
                              <div className="flex items-center gap-2 mb-2">
                                <ShieldCheckIcon className="w-4 h-4 text-green-500" />
                                <span className="text-xs font-medium text-gray-600">Confidence</span>
                              </div>
                              <div className="text-xl font-bold text-gray-900">{Math.round(prediction.confidence_score * 100)}%</div>
                              <div className="text-xs text-gray-500 mt-1">
                                {prediction.confidence_score >= 0.8 ? 'High accuracy' :
                                 prediction.confidence_score >= 0.6 ? 'Moderate' : 'Low accuracy'}
                              </div>
                            </div>

                            {/* Temp */}
                            <div className="bg-white p-4 rounded-lg border border-gray-200">
                              <div className="flex items-center gap-2 mb-2">
                                <ThermometerIcon className="w-4 h-4 text-orange-500" />
                                <span className="text-xs font-medium text-gray-600">Temp</span>
                              </div>
                              <div className="text-xl font-bold text-gray-900">{prediction.weather_data.temperature}°C</div>
                              <div className="text-xs text-gray-500 mt-1">{tempDescription}</div>
                            </div>

                            {/* Air Humidity */}
                            <div className="bg-white p-4 rounded-lg border border-gray-200">
                              <div className="flex items-center gap-2 mb-2">
                                <CloudRainIcon className="w-4 h-4 text-cyan-500" />
                                <span className="text-xs font-medium text-gray-600">Air Humidity</span>
                              </div>
                              <div className="text-xl font-bold text-gray-900">{prediction.weather_data.humidity}%</div>
                              <div className="text-xs text-gray-500 mt-1">{humidityDescription}</div>
                            </div>
                          </div>

                          {/* Calculation Context */}
                          {prediction.field_info?.area_hectares && (
                            <div className="px-6 py-4 bg-gray-100 border-t border-gray-200">
                              <div className="text-sm text-gray-700">
                                <span className="font-medium">Field Size:</span> {prediction.field_info.area_hectares} hectare{prediction.field_info.area_hectares !== 1 ? 's' : ''}
                                {prediction.total_water_liters && (
                                  <>
                                    <span className="mx-2">|</span>
                                    <span className="font-medium">Total Volume:</span> ~{prediction.total_water_liters.toLocaleString()} liters
                                  </>
                                )}
                              </div>
                            </div>
                          )}

                          {/* Actions */}
                          <div className="px-6 py-4 bg-white border-t border-gray-200">
                            <div className="flex items-center gap-3 flex-wrap">
                              {prediction.field_info && (
                                <details className="group">
                                  <summary className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors cursor-pointer list-none">
                                    <ChevronDownIcon className="w-4 h-4 group-open:rotate-180 transition-transform" />
                                    View Field Details
                                  </summary>
                                  <div className="absolute mt-2 p-4 bg-white rounded-lg shadow-lg border border-gray-200 z-10 grid grid-cols-2 gap-3 text-sm min-w-[300px]">
                                    <div><span className="text-gray-500">Crop:</span> <span className="font-medium">{prediction.field_info.crop_type}</span></div>
                                    <div><span className="text-gray-500">Days planted:</span> <span className="font-medium">{prediction.field_info.crop_days}</span></div>
                                    <div><span className="text-gray-500">Ground moisture:</span> <span className="font-medium">{prediction.field_info.soil_moisture}%</span></div>
                                    <div><span className="text-gray-500">Soil type:</span> <span className="font-medium">{prediction.field_info.soil_type}</span></div>
                                    <div><span className="text-gray-500">Region:</span> <span className="font-medium">{prediction.field_info.region}</span></div>
                                    <div><span className="text-gray-500">Season:</span> <span className="font-medium">{prediction.field_info.season}</span></div>
                                  </div>
                                </details>
                              )}
                              <button 
                                onClick={() => window.location.href = `/fields/${prediction.field_id}`}
                                className="px-4 py-2 text-sm text-gray-700 border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors"
                              >
                                View Field
                              </button>
                              <button 
                                onClick={() => generateScheduleForField(prediction.field_id, prediction.field_name)}
                                disabled={generatingForField === prediction.field_id}
                                className={`px-6 py-2 text-sm font-semibold text-white ${config.button} rounded-lg transition-colors ml-auto disabled:opacity-50 flex items-center gap-2`}
                              >
                                {generatingForField === prediction.field_id ? (
                                  <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                    Creating...
                                  </>
                                ) : (
                                  'Create Irrigation Schedule'
                                )}
                              </button>
                            </div>
                          </div>
                        </div>

                        {/* Mobile Card - Vertical Layout */}
                        <div className="md:hidden border border-gray-200 rounded-xl overflow-hidden shadow-lg">
                          {/* Hero Section */}
                          <div className={`bg-gradient-to-br ${config.gradient} px-6 py-6 text-white`}>
                            <div className="flex items-start justify-between mb-3">
                              <h2 className="text-2xl font-bold">{prediction.field_name}</h2>
                              <span className="text-2xl">
                                {prediction.priority === 'critical' ? '⚠️' :
                                 prediction.priority === 'high' ? '🔔' :
                                 prediction.priority === 'medium' ? '📋' : '✅'}
                              </span>
                            </div>
                            <p className="text-lg font-medium opacity-95">
                              {config.label}
                            </p>
                            <p className="text-sm opacity-80 mt-1">
                              {prediction.priority_description || 'Review recommendation below'}
                            </p>
                          </div>

                          {/* Data Sections */}
                          <div className="bg-white px-6 py-5 space-y-4">
                            {/* Weather */}
                            <div className="pb-4 border-b border-gray-200">
                              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Weather Conditions</div>
                              <div className="flex items-center gap-6">
                                <div className="flex items-center gap-2">
                                  <ThermometerIcon className="w-5 h-5 text-orange-500" />
                                  <div>
                                    <div className="text-lg font-bold text-gray-900">{prediction.weather_data.temperature}°C</div>
                                    <div className="text-xs text-gray-500">{tempDescription}</div>
                                  </div>
                                </div>
                                <div className="flex items-center gap-2">
                                  <CloudRainIcon className="w-5 h-5 text-cyan-500" />
                                  <div>
                                    <div className="text-lg font-bold text-gray-900">{prediction.weather_data.humidity}%</div>
                                    <div className="text-xs text-gray-500">Air Humidity</div>
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* AI Confidence */}
                            <div className="pb-4 border-b border-gray-200">
                              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">AI Confidence</div>
                              <div className="flex items-center gap-2">
                                <ShieldCheckIcon className="w-5 h-5 text-green-500" />
                                <span className="text-lg font-bold text-gray-900">{Math.round(prediction.confidence_score * 100)}%</span>
                                <span className="text-sm text-gray-600">
                                  {prediction.confidence_score >= 0.8 ? 'High accuracy' :
                                   prediction.confidence_score >= 0.6 ? 'Moderate' : 'Low accuracy'}
                                </span>
                              </div>
                            </div>

                            {/* Recommendation */}
                            <div>
                              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Recommendation</div>
                              <div className="space-y-2">
                                <div className="flex items-start gap-2">
                                  <DropletIcon className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                                  <div>
                                    <div className="text-sm font-medium text-gray-900">Rate: {prediction.predicted_water_amount.toFixed(1)} L/m²</div>
                                    {prediction.field_info?.area_hectares && prediction.total_water_liters && (
                                      <div className="text-xs text-gray-600 mt-1">
                                        Field ({prediction.field_info.area_hectares} ha): ~{prediction.total_water_liters.toLocaleString()} Liters ({totalWaterDisplay})
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Action Area */}
                          <div className="bg-gray-50 px-6 py-4 space-y-3">
                            {prediction.field_info && (
                              <details className="group">
                                <summary className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors border border-gray-200 bg-white cursor-pointer list-none">
                                  <ChevronDownIcon className="w-4 h-4 group-open:rotate-180 transition-transform" />
                                  View Field Details
                                </summary>
                                <div className="mt-2 p-3 bg-white rounded-lg border border-gray-200 grid grid-cols-2 gap-2 text-xs">
                                  <div><span className="text-gray-500">Crop:</span> <span className="font-medium">{prediction.field_info.crop_type}</span></div>
                                  <div><span className="text-gray-500">Days:</span> <span className="font-medium">{prediction.field_info.crop_days}</span></div>
                                  <div><span className="text-gray-500">Ground:</span> <span className="font-medium">{prediction.field_info.soil_moisture}%</span></div>
                                  <div><span className="text-gray-500">Soil:</span> <span className="font-medium">{prediction.field_info.soil_type}</span></div>
                                  <div><span className="text-gray-500">Region:</span> <span className="font-medium">{prediction.field_info.region}</span></div>
                                  <div><span className="text-gray-500">Season:</span> <span className="font-medium">{prediction.field_info.season}</span></div>
                                </div>
                              </details>
                            )}
                            <button 
                              onClick={() => generateScheduleForField(prediction.field_id, prediction.field_name)}
                              disabled={generatingForField === prediction.field_id}
                              className={`w-full px-6 py-3 text-base font-semibold text-white ${config.button} rounded-lg transition-colors shadow-md disabled:opacity-50 flex items-center justify-center gap-2`}
                            >
                              {generatingForField === prediction.field_id ? (
                                <>
                                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                  Creating Schedule...
                                </>
                              ) : (
                                'Create Irrigation Schedule'
                              )}
                            </button>
                            <button 
                              onClick={() => window.location.href = `/fields/${prediction.field_id}`}
                              className="w-full text-sm text-gray-600 hover:text-gray-900 transition-colors py-2"
                            >
                              View Field
                            </button>
                          </div>

                          {/* Timestamp */}
                          <div className="bg-white px-6 py-3 border-t border-gray-200">
                            <p className="text-xs text-gray-500 text-center">
                              Updated: {new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* Quick Actions */}
          <div className="bg-white rounded-xl shadow p-6 mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button 
                onClick={() => window.location.href = '/fields/new'}
                className="p-5 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all text-left"
              >
                <h4 className="text-lg font-bold text-gray-900 mb-2">Add New Field</h4>
                <p className="text-base text-gray-600">Register a new field for irrigation scheduling</p>
              </button>
              <button
                onClick={() => window.location.href = '/schedules'}
                className="p-5 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all text-left"
              >
                <h4 className="text-lg font-bold text-gray-900 mb-2">View Schedules</h4>
                <p className="text-base text-gray-600">Manage your irrigation schedules</p>
              </button>
              <button
                onClick={() => window.location.href = '/history'}
                className="p-5 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-all text-left"
              >
                <h4 className="text-lg font-bold text-gray-900 mb-2">View History</h4>
                <p className="text-base text-gray-600">Track your past irrigation activities</p>
              </button>
            </div>
          </div>

          {/* Help Section */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
            <h3 className="text-lg font-bold text-blue-900 mb-2">Need Help?</h3>
            <p className="text-base text-blue-800">
              This system uses weather data and soil information to recommend when and how much to water your crops.
              {fields.length === 0 ? ' Start by adding your first field above.' :
               predictions.length === 0 ? ' Your fields are being analyzed.' :
               ' Review the recommendations above and create irrigation schedules for your fields.'}
            </p>
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
