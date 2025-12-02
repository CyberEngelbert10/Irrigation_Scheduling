import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { fieldAPI } from '@/lib/api';
import { Field } from '@/types/field';
import Navigation from '@/components/Navigation';
import AuthGuard from '@/components/auth/AuthGuard';

export default function FieldDetailPage() {
  const router = useRouter();
  const { id } = router.query;
  const [field, setField] = useState<Field | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showMoistureModal, setShowMoistureModal] = useState(false);
  const [moistureValue, setMoistureValue] = useState(0);
  const [updatingMoisture, setUpdatingMoisture] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(false);

  useEffect(() => {
    if (id) {
      fetchField();
    }
  }, [id]);

  const fetchField = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await fieldAPI.get(Number(id));
      setField(data);
      setMoistureValue(data.current_soil_moisture);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load field details');
      console.error('Error fetching field:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateMoisture = async () => {
    if (!field) return;
    
    try {
      setUpdatingMoisture(true);
      const updated = await fieldAPI.updateMoisture(field.id, moistureValue);
      setField(updated);
      setShowMoistureModal(false);
      alert('Soil moisture updated successfully!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update soil moisture');
    } finally {
      setUpdatingMoisture(false);
    }
  };

  const handleDelete = async () => {
    if (!field) return;
    
    try {
      await fieldAPI.delete(field.id);
      alert('Field deleted successfully!');
      router.push('/fields');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete field');
    }
  };

  if (loading) {
    return (
      <AuthGuard>
        <div className="min-h-screen bg-gray-50">
          <Navigation currentPage="fields" />
          <div className="flex items-center justify-center py-24">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
              <p className="mt-4 text-gray-600">Loading field details...</p>
            </div>
          </div>
        </div>
      </AuthGuard>
    );
  }

  if (error || !field) {
    return (
      <AuthGuard>
        <div className="min-h-screen bg-gray-50">
          <Navigation currentPage="fields" />
          <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-sm text-red-800">{error || 'Field not found'}</p>
            </div>
            <div className="mt-4">
              <Link href="/fields" className="text-green-600 hover:text-green-700">
                ← Back to Fields
              </Link>
            </div>
          </div>
        </div>
      </AuthGuard>
    );
  }

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Navigation currentPage="fields" />
        
        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Breadcrumb */}
          <nav className="flex mb-8" aria-label="Breadcrumb">
            <ol className="flex items-center space-x-4">
              <li>
                <Link href="/dashboard" className="text-gray-400 hover:text-gray-500">
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                  </svg>
                  <span className="sr-only">Dashboard</span>
                </Link>
              </li>
              <li>
                <div className="flex items-center">
                  <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                  <Link href="/fields" className="ml-4 text-sm font-medium text-gray-500 hover:text-gray-700">
                    Fields
                  </Link>
                </div>
              </li>
              <li>
                <div className="flex items-center">
                  <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                  <span className="ml-4 text-sm font-medium text-gray-500">{field.name}</span>
                </div>
            </li>
          </ol>
        </nav>

        {/* Header */}
        <div className="md:flex md:items-center md:justify-between mb-6">
          <div className="flex-1 min-w-0">
            <h1 className="text-3xl font-bold text-gray-900">{field.name}</h1>
            <div className="mt-2 flex items-center">
              {field.is_active ? (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                  Active
                </span>
              ) : (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                  Inactive
                </span>
              )}
            </div>
          </div>
          <div className="mt-4 flex space-x-3 md:mt-0 md:ml-4">
            <button
              onClick={() => setShowMoistureModal(true)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Update Moisture
            </button>
            <Link
              href={`/fields/${field.id}/edit`}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              Edit Field
            </Link>
            <button
              onClick={() => setDeleteConfirm(true)}
              className="inline-flex items-center px-4 py-2 border border-red-300 shadow-sm text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50"
            >
              Delete
            </button>
          </div>
        </div>

        {/* Field Details */}
        <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
          {/* Basic Information */}
          <div className="px-6 py-5 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Basic Information</h2>
          </div>
          <div className="px-6 py-5">
            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Field Name</dt>
                <dd className="mt-1 text-sm text-gray-900">{field.name}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1 text-sm text-gray-900">{field.is_active ? 'Active' : 'Inactive'}</dd>
              </div>
              {field.location && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Location</dt>
                  <dd className="mt-1 text-sm text-gray-900">{field.location}</dd>
                </div>
              )}
              <div>
                <dt className="text-sm font-medium text-gray-500">Region</dt>
                <dd className="mt-1 text-sm text-gray-900">{field.region_display}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Area</dt>
                <dd className="mt-1 text-sm text-gray-900">{field.area} hectares</dd>
              </div>
              {field.latitude && field.longitude && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Coordinates</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {parseFloat(String(field.latitude)).toFixed(6)}, {parseFloat(String(field.longitude)).toFixed(6)}
                  </dd>
                </div>
              )}
            </dl>
          </div>

          {/* Crop Details */}
          <div className="px-6 py-5 border-t border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Crop Details</h2>
            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Crop Type</dt>
                <dd className="mt-1 text-sm text-gray-900">{field.crop_type_display}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Current Season</dt>
                <dd className="mt-1 text-sm text-gray-900">{field.season_display}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Planting Date</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(field.planting_date).toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Crop Age</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {field.crop_days} days ({field.crop_age_weeks} weeks)
                </dd>
              </div>
            </dl>
          </div>

          {/* Soil & Irrigation */}
          <div className="px-6 py-5 border-t border-gray-200">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Soil & Irrigation</h2>
            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Soil Type</dt>
                <dd className="mt-1 text-sm text-gray-900">{field.soil_type_display}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Current Soil Moisture</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <div className="flex items-center">
                    <span className="text-lg font-semibold text-green-600">{field.current_soil_moisture}%</span>
                    <div className="ml-3 flex-1">
                      <div className="bg-gray-200 rounded-full h-2 w-24">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${field.current_soil_moisture}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Irrigation Method</dt>
                <dd className="mt-1 text-sm text-gray-900">{field.irrigation_method_display}</dd>
              </div>
            </dl>
          </div>

          {/* Notes */}
          {field.notes && (
            <div className="px-6 py-5 border-t border-gray-200">
              <h2 className="text-lg font-medium text-gray-900 mb-2">Notes</h2>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{field.notes}</p>
            </div>
          )}

          {/* Metadata */}
          <div className="px-6 py-5 border-t border-gray-200 bg-gray-50">
            <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Created</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(field.created_at).toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(field.updated_at).toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </dd>
              </div>
            </dl>
          </div>
        </div>

        {/* Update Moisture Modal */}
        {showMoistureModal && (
          <div className="fixed z-10 inset-0 overflow-y-auto">
            <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
              <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowMoistureModal(false)}></div>
              
              <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
                <div>
                  <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                    <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
                    </svg>
                  </div>
                  <div className="mt-3 text-center sm:mt-5">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Update Soil Moisture</h3>
                    <div className="mt-4">
                      <label htmlFor="moisture" className="block text-sm font-medium text-gray-700 text-left mb-2">
                        Current Soil Moisture (%)
                      </label>
                      <input
                        type="number"
                        id="moisture"
                        value={moistureValue}
                        onChange={(e) => setMoistureValue(Number(e.target.value))}
                        min="0"
                        max="100"
                        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm"
                      />
                      <p className="mt-2 text-sm text-gray-500">Enter a value between 0 and 100</p>
                    </div>
                  </div>
                </div>
                <div className="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
                  <button
                    type="button"
                    disabled={updatingMoisture || moistureValue < 0 || moistureValue > 100}
                    onClick={handleUpdateMoisture}
                    className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:col-start-2 sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {updatingMoisture ? 'Updating...' : 'Update'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowMoistureModal(false)}
                    className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:mt-0 sm:col-start-1 sm:text-sm"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {deleteConfirm && (
          <div className="fixed z-10 inset-0 overflow-y-auto">
            <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
              <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setDeleteConfirm(false)}></div>
              
              <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
                <div className="sm:flex sm:items-start">
                  <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                    <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Delete Field</h3>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500">
                        Are you sure you want to delete <strong>{field.name}</strong>? This action cannot be undone.
                      </p>
                    </div>
                  </div>
                </div>
                <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                  <button
                    type="button"
                    onClick={handleDelete}
                    className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm"
                  >
                    Delete
                  </button>
                  <button
                    type="button"
                    onClick={() => setDeleteConfirm(false)}
                    className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:mt-0 sm:w-auto sm:text-sm"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        </main>
      </div>
    </AuthGuard>
  );
}
