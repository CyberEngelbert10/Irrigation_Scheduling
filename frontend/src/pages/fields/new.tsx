import { useState, FormEvent } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { fieldAPI } from '@/lib/api';
import { FieldCreateData, REGIONS, CROPS, SOIL_TYPES, IRRIGATION_METHODS, SEASONS } from '@/types/field';

export default function NewFieldPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const [formData, setFormData] = useState<FieldCreateData>({
    name: '',
    location: '',
    region: '',
    latitude: undefined,
    longitude: undefined,
    area: 0,
    crop_type: '',
    planting_date: '',
    soil_type: '',
    current_soil_moisture: 50,
    irrigation_method: '',
    current_season: '',
    notes: '',
    is_active: true,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else if (type === 'number') {
      const numValue = value === '' ? undefined : parseFloat(value);
      setFormData(prev => ({ ...prev, [name]: numValue }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Field name is required';
    } else if (formData.name.length > 255) {
      newErrors.name = 'Field name must be less than 255 characters';
    }

    if (!formData.region) {
      newErrors.region = 'Region is required';
    }

    if (!formData.area || formData.area <= 0) {
      newErrors.area = 'Area must be greater than 0';
    }

    if (!formData.crop_type) {
      newErrors.crop_type = 'Crop type is required';
    }

    if (!formData.planting_date) {
      newErrors.planting_date = 'Planting date is required';
    } else {
      const plantingDate = new Date(formData.planting_date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (plantingDate > today) {
        newErrors.planting_date = 'Planting date cannot be in the future';
      }
    }

    if (!formData.soil_type) {
      newErrors.soil_type = 'Soil type is required';
    }

    if (formData.current_soil_moisture < 0 || formData.current_soil_moisture > 100) {
      newErrors.current_soil_moisture = 'Soil moisture must be between 0 and 100';
    }

    if (!formData.irrigation_method) {
      newErrors.irrigation_method = 'Irrigation method is required';
    }

    if (!formData.current_season) {
      newErrors.current_season = 'Season is required';
    }

    if (formData.latitude !== undefined && (formData.latitude < -90 || formData.latitude > 90)) {
      newErrors.latitude = 'Latitude must be between -90 and 90';
    }

    if (formData.longitude !== undefined && (formData.longitude < -180 || formData.longitude > 180)) {
      newErrors.longitude = 'Longitude must be between -180 and 180';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setErrors({});
      
      // Prepare data for submission
      const submitData = {
        ...formData,
        location: formData.location || undefined,
        latitude: formData.latitude || undefined,
        longitude: formData.longitude || undefined,
        notes: formData.notes || undefined,
      };

      await fieldAPI.create(submitData);
      
      // Success - redirect to fields list
      alert('Field created successfully!');
      router.push('/fields');
    } catch (err: any) {
      console.error('Error creating field:', err);
      
      // Handle validation errors from backend
      if (err.response?.data) {
        const backendErrors: Record<string, string> = {};
        Object.keys(err.response.data).forEach(key => {
          const errorValue = err.response.data[key];
          backendErrors[key] = Array.isArray(errorValue) ? errorValue[0] : errorValue;
        });
        setErrors(backendErrors);
      } else {
        setErrors({ general: 'Failed to create field. Please try again.' });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/fields" className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-4">
            <svg className="mr-1 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Fields
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Add New Field</h1>
          <p className="mt-2 text-sm text-gray-600">
            Enter the details of your agricultural field
          </p>
        </div>

        {/* General Error */}
        {errors.general && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-800">{errors.general}</p>
              </div>
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white shadow rounded-lg">
          <div className="px-6 py-6 space-y-6">
            {/* Basic Information */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h2>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                {/* Field Name */}
                <div className="sm:col-span-2">
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Field Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm ${
                      errors.name ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="e.g., North Field, Main Maize Field"
                  />
                  {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
                </div>

                {/* Location */}
                <div className="sm:col-span-2">
                  <label htmlFor="location" className="block text-sm font-medium text-gray-700">
                    Location Description
                  </label>
                  <input
                    type="text"
                    id="location"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
                    placeholder="e.g., Chilanga, Near water source"
                  />
                </div>

                {/* Region */}
                <div>
                  <label htmlFor="region" className="block text-sm font-medium text-gray-700">
                    Region <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="region"
                    name="region"
                    value={formData.region}
                    onChange={handleChange}
                    className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm ${
                      errors.region ? 'border-red-300' : 'border-gray-300'
                    }`}
                  >
                    <option value="">Select a region</option>
                    {REGIONS.map(region => (
                      <option key={region.value} value={region.value}>{region.label}</option>
                    ))}
                  </select>
                  {errors.region && <p className="mt-1 text-sm text-red-600">{errors.region}</p>}
                </div>

                {/* Area */}
                <div>
                  <label htmlFor="area" className="block text-sm font-medium text-gray-700">
                    Area (hectares) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    id="area"
                    name="area"
                    value={formData.area || ''}
                    onChange={handleChange}
                    step="0.01"
                    min="0.01"
                    className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm ${
                      errors.area ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="e.g., 2.5"
                  />
                  {errors.area && <p className="mt-1 text-sm text-red-600">{errors.area}</p>}
                </div>

                {/* Latitude */}
                <div>
                  <label htmlFor="latitude" className="block text-sm font-medium text-gray-700">
                    Latitude (optional)
                  </label>
                  <input
                    type="number"
                    id="latitude"
                    name="latitude"
                    value={formData.latitude || ''}
                    onChange={handleChange}
                    step="0.000001"
                    min="-90"
                    max="90"
                    className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm ${
                      errors.latitude ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="e.g., -15.416667"
                  />
                  {errors.latitude && <p className="mt-1 text-sm text-red-600">{errors.latitude}</p>}
                </div>

                {/* Longitude */}
                <div>
                  <label htmlFor="longitude" className="block text-sm font-medium text-gray-700">
                    Longitude (optional)
                  </label>
                  <input
                    type="number"
                    id="longitude"
                    name="longitude"
                    value={formData.longitude || ''}
                    onChange={handleChange}
                    step="0.000001"
                    min="-180"
                    max="180"
                    className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm ${
                      errors.longitude ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="e.g., 28.283333"
                  />
                  {errors.longitude && <p className="mt-1 text-sm text-red-600">{errors.longitude}</p>}
                </div>
              </div>
            </div>

            {/* Crop Information */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Crop Information</h2>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                {/* Crop Type */}
                <div>
                  <label htmlFor="crop_type" className="block text-sm font-medium text-gray-700">
                    Crop Type <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="crop_type"
                    name="crop_type"
                    value={formData.crop_type}
                    onChange={handleChange}
                    className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm ${
                      errors.crop_type ? 'border-red-300' : 'border-gray-300'
                    }`}
                  >
                    <option value="">Select a crop</option>
                    {CROPS.map(crop => (
                      <option key={crop.value} value={crop.value}>{crop.label}</option>
                    ))}
                  </select>
                  {errors.crop_type && <p className="mt-1 text-sm text-red-600">{errors.crop_type}</p>}
                </div>

                {/* Planting Date */}
                <div>
                  <label htmlFor="planting_date" className="block text-sm font-medium text-gray-700">
                    Planting Date <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    id="planting_date"
                    name="planting_date"
                    value={formData.planting_date}
                    onChange={handleChange}
                    max={new Date().toISOString().split('T')[0]}
                    className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm ${
                      errors.planting_date ? 'border-red-300' : 'border-gray-300'
                    }`}
                  />
                  {errors.planting_date && <p className="mt-1 text-sm text-red-600">{errors.planting_date}</p>}
                </div>

                {/* Season */}
                <div>
                  <label htmlFor="current_season" className="block text-sm font-medium text-gray-700">
                    Current Season <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="current_season"
                    name="current_season"
                    value={formData.current_season}
                    onChange={handleChange}
                    className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm ${
                      errors.current_season ? 'border-red-300' : 'border-gray-300'
                    }`}
                  >
                    <option value="">Select a season</option>
                    {SEASONS.map(season => (
                      <option key={season.value} value={season.value}>{season.label}</option>
                    ))}
                  </select>
                  {errors.current_season && <p className="mt-1 text-sm text-red-600">{errors.current_season}</p>}
                </div>
              </div>
            </div>

            {/* Soil & Irrigation */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Soil & Irrigation</h2>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                {/* Soil Type */}
                <div>
                  <label htmlFor="soil_type" className="block text-sm font-medium text-gray-700">
                    Soil Type <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="soil_type"
                    name="soil_type"
                    value={formData.soil_type}
                    onChange={handleChange}
                    className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm ${
                      errors.soil_type ? 'border-red-300' : 'border-gray-300'
                    }`}
                  >
                    <option value="">Select soil type</option>
                    {SOIL_TYPES.map(soil => (
                      <option key={soil.value} value={soil.value}>{soil.label}</option>
                    ))}
                  </select>
                  {errors.soil_type && <p className="mt-1 text-sm text-red-600">{errors.soil_type}</p>}
                </div>

                {/* Soil Moisture */}
                <div>
                  <label htmlFor="current_soil_moisture" className="block text-sm font-medium text-gray-700">
                    Current Soil Moisture (%) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    id="current_soil_moisture"
                    name="current_soil_moisture"
                    value={formData.current_soil_moisture}
                    onChange={handleChange}
                    min="0"
                    max="100"
                    className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm ${
                      errors.current_soil_moisture ? 'border-red-300' : 'border-gray-300'
                    }`}
                  />
                  <p className="mt-1 text-xs text-gray-500">Enter a value between 0 and 100</p>
                  {errors.current_soil_moisture && <p className="mt-1 text-sm text-red-600">{errors.current_soil_moisture}</p>}
                </div>

                {/* Irrigation Method */}
                <div>
                  <label htmlFor="irrigation_method" className="block text-sm font-medium text-gray-700">
                    Irrigation Method <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="irrigation_method"
                    name="irrigation_method"
                    value={formData.irrigation_method}
                    onChange={handleChange}
                    className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm ${
                      errors.irrigation_method ? 'border-red-300' : 'border-gray-300'
                    }`}
                  >
                    <option value="">Select irrigation method</option>
                    {IRRIGATION_METHODS.map(method => (
                      <option key={method.value} value={method.value}>{method.label}</option>
                    ))}
                  </select>
                  {errors.irrigation_method && <p className="mt-1 text-sm text-red-600">{errors.irrigation_method}</p>}
                </div>
              </div>
            </div>

            {/* Additional Information */}
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Additional Information</h2>
              
              {/* Notes */}
              <div className="mb-4">
                <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
                  Notes
                </label>
                <textarea
                  id="notes"
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows={3}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
                  placeholder="Any additional information about this field..."
                />
              </div>

              {/* Active Status */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleChange}
                  className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700">
                  Field is active
                </label>
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
            <Link
              href="/fields"
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating...
                </>
              ) : (
                'Create Field'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
