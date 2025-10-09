import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { settingsAPI } from '@/lib/api';
import { UserPreferences } from '@/types/predictions';
import Navigation from '@/components/Navigation';
import { toast } from 'react-hot-toast';

export default function Settings() {
  const { user } = useAuth();
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [resetting, setResetting] = useState(false);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const data = await settingsAPI.getPreferences();
      setPreferences(data);
    } catch (error) {
      console.error('Failed to load preferences:', error);
      toast.error('Failed to load preferences');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!preferences) return;

    setSaving(true);
    try {
      const updated = await settingsAPI.updatePreferences(preferences);
      setPreferences(updated);
      toast.success('Settings saved successfully');
    } catch (error) {
      console.error('Failed to save preferences:', error);
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    if (!confirm('Are you sure you want to reset all preferences to defaults?')) return;

    setResetting(true);
    try {
      const reset = await settingsAPI.resetPreferences();
      setPreferences(reset);
      toast.success('Settings reset to defaults');
    } catch (error) {
      console.error('Failed to reset preferences:', error);
      toast.error('Failed to reset settings');
    } finally {
      setResetting(false);
    }
  };

  const updatePreference = (field: keyof UserPreferences, value: any) => {
    if (!preferences) return;
    setPreferences({ ...preferences, [field]: value });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation currentPage="settings" />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="text-center">Loading settings...</div>
        </div>
      </div>
    );
  }

  if (!preferences) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navigation currentPage="settings" />
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="text-center text-red-600">Failed to load settings</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation currentPage="settings" />

      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600 mt-1">Customize your irrigation management preferences</p>
          </div>

          <div className="p-6 space-y-8">
            {/* Notification Preferences */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Notifications</h2>
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={preferences.email_notifications}
                    onChange={(e) => updatePreference('email_notifications', e.target.checked)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-3 text-sm text-gray-700">Email notifications</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={preferences.push_notifications}
                    onChange={(e) => updatePreference('push_notifications', e.target.checked)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-3 text-sm text-gray-700">Push notifications</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={preferences.irrigation_reminders}
                    onChange={(e) => updatePreference('irrigation_reminders', e.target.checked)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-3 text-sm text-gray-700">Irrigation reminders</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={preferences.weather_alerts}
                    onChange={(e) => updatePreference('weather_alerts', e.target.checked)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-3 text-sm text-gray-700">Weather alerts</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={preferences.weekly_reports}
                    onChange={(e) => updatePreference('weekly_reports', e.target.checked)}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-3 text-sm text-gray-700">Weekly reports</span>
                </label>
              </div>
            </div>

            {/* Unit Preferences */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Units</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Temperature Unit</label>
                  <select
                    value={preferences.temperature_unit}
                    onChange={(e) => updatePreference('temperature_unit', e.target.value as 'celsius' | 'fahrenheit')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="celsius">Celsius (°C)</option>
                    <option value="fahrenheit">Fahrenheit (°F)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Volume Unit</label>
                  <select
                    value={preferences.volume_unit}
                    onChange={(e) => updatePreference('volume_unit', e.target.value as 'liters' | 'gallons')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="liters">Liters (L)</option>
                    <option value="gallons">Gallons (gal)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Irrigation Defaults */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Irrigation Defaults</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Default Method</label>
                  <select
                    value={preferences.default_irrigation_method}
                    onChange={(e) => updatePreference('default_irrigation_method', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="drip">Drip</option>
                    <option value="sprinkler">Sprinkler</option>
                    <option value="flood">Flood</option>
                    <option value="manual">Manual</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Default Duration (minutes)</label>
                  <input
                    type="number"
                    min="1"
                    max="480"
                    value={preferences.default_irrigation_duration}
                    onChange={(e) => updatePreference('default_irrigation_duration', parseInt(e.target.value) || 30)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Default Water Amount ({preferences.volume_unit === 'liters' ? 'L' : 'gal'})
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    value={preferences.default_water_amount}
                    onChange={(e) => updatePreference('default_water_amount', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              </div>
            </div>

            {/* Display Preferences */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Display Preferences</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Dashboard Refresh Interval (minutes)</label>
                  <input
                    type="number"
                    min="1"
                    max="60"
                    value={preferences.dashboard_refresh_interval}
                    onChange={(e) => updatePreference('dashboard_refresh_interval', parseInt(e.target.value) || 5)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Items Per Page</label>
                  <select
                    value={preferences.items_per_page}
                    onChange={(e) => updatePreference('items_per_page', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="10">10</option>
                    <option value="25">25</option>
                    <option value="50">50</option>
                    <option value="100">100</option>
                  </select>
                </div>
              </div>
            </div>

            {/* System Preferences */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">System Preferences</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
                  <select
                    value={preferences.timezone}
                    onChange={(e) => updatePreference('timezone', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="UTC">UTC</option>
                    <option value="Africa/Lusaka">Lusaka (CAT)</option>
                    <option value="Africa/Harare">Harare (CAT)</option>
                    <option value="Africa/Johannesburg">Johannesburg (SAST)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
                  <select
                    value={preferences.language}
                    onChange={(e) => updatePreference('language', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="en">English</option>
                    <option value="en-ZM">English (Zambia)</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex justify-between">
            <button
              onClick={handleReset}
              disabled={resetting}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50"
            >
              {resetting ? 'Resetting...' : 'Reset to Defaults'}
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-6 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}