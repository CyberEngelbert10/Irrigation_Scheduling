import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AuthGuard from '@/components/auth/AuthGuard';
import Navigation from '@/components/Navigation';
import { predictionsAPI, fieldAPI } from '@/lib/api';
import { IrrigationHistory } from '@/types/predictions';
import { Field } from '@/types/field';

export default function History() {
  const { user } = useAuth();
  const [history, setHistory] = useState<IrrigationHistory[]>([]);
  const [fields, setFields] = useState<Field[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedField, setSelectedField] = useState<number | 'all'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    loadData();
  }, [selectedField, currentPage]);

  const loadData = async () => {
    try {
      setLoading(true);

      // Load fields for filter dropdown
      if (fields.length === 0) {
        const fieldsData = await fieldAPI.list({ is_active: true });
        setFields(fieldsData);
      }

      // Load history with filters
      const params: any = {
        limit: itemsPerPage,
        offset: (currentPage - 1) * itemsPerPage,
      };

      if (selectedField !== 'all') {
        params.field_id = selectedField;
      }

      const historyData = await predictionsAPI.getHistory(params);
      setHistory(historyData.results || historyData);
      setTotalPages(Math.ceil((historyData.count || historyData.length) / itemsPerPage));
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatTime = (timeString: string) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getMethodIcon = (method: string) => {
    switch (method) {
      case 'drip': return '💧';
      case 'sprinkler': return '🌊';
      case 'flood': return '🌊';
      case 'manual': return '🚿';
      default: return '💦';
    }
  };

  const getRatingStars = (rating?: number) => {
    if (!rating) return 'Not rated';
    return '⭐'.repeat(rating) + '☆'.repeat(5 - rating);
  };

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Navigation currentPage="history" />

        <main className="max-w-7xl mx-auto px-4 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">📚 Irrigation History</h1>
            <p className="text-gray-600">Track your past irrigation activities and water usage</p>
          </div>

          {/* Filters */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
              <div className="flex-1">
                <label htmlFor="field-filter" className="block text-sm font-medium text-gray-700 mb-1">
                  Filter by Field
                </label>
                <select
                  id="field-filter"
                  value={selectedField}
                  onChange={(e) => {
                    setSelectedField(e.target.value === 'all' ? 'all' : parseInt(e.target.value));
                    setCurrentPage(1);
                  }}
                  className="w-full sm:w-64 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="all">All Fields</option>
                  {fields.map((field) => (
                    <option key={field.id} value={field.id}>
                      {field.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="text-sm text-gray-500">
                Showing {history.length} records
              </div>
            </div>
          </div>

          {/* History List */}
          {loading ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                <span className="ml-3 text-gray-600">Loading history...</span>
              </div>
            </div>
          ) : history.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
              <div className="text-gray-400 mb-4">
                <span className="text-4xl">📭</span>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No irrigation history yet</h3>
              <p className="text-gray-600">
                Your irrigation activities will appear here once you start recording them.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {history.map((record) => (
                <div key={record.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="font-semibold text-gray-900">{record.field_name}</h3>
                        <span className="text-sm text-gray-500">
                          {formatDate(record.irrigation_date)} at {formatTime(record.irrigation_time)}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div>
                          <p className="text-xs text-gray-500">Water Used</p>
                          <p className="font-semibold text-gray-900">{record.water_amount_used}L</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Duration</p>
                          <p className="font-semibold text-gray-900">{record.duration_minutes} min</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Method</p>
                          <p className="font-semibold text-gray-900 flex items-center gap-1">
                            <span>{getMethodIcon(record.irrigation_method)}</span>
                            {record.irrigation_method}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Effectiveness</p>
                          <p className="font-semibold text-gray-900 text-sm">
                            {getRatingStars(record.effectiveness_rating)}
                          </p>
                        </div>
                      </div>

                      {record.soil_moisture_before && record.soil_moisture_after && (
                        <div className="mb-3">
                          <p className="text-xs text-gray-500 mb-1">Soil Moisture Change</p>
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">{record.soil_moisture_before}%</span>
                            <span className="text-gray-400">→</span>
                            <span className="text-sm font-medium">{record.soil_moisture_after}%</span>
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              record.soil_moisture_after > record.soil_moisture_before
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {record.soil_moisture_after > record.soil_moisture_before ? '+' : ''}
                              {(record.soil_moisture_after - record.soil_moisture_before).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      )}

                      {record.notes && (
                        <div className="mb-3">
                          <p className="text-xs text-gray-500 mb-1">Notes</p>
                          <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded">{record.notes}</p>
                        </div>
                      )}

                      {record.related_schedule && (
                        <div className="text-xs text-gray-500">
                          Related to schedule #{record.related_schedule}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-8 flex justify-center">
              <nav className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>

                <span className="px-4 py-2 text-sm text-gray-700">
                  Page {currentPage} of {totalPages}
                </span>

                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </nav>
            </div>
          )}
        </main>
      </div>
    </AuthGuard>
  );
}