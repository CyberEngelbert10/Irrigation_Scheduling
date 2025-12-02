import { useState, useEffect } from 'react';
import Link from 'next/link';
import Navigation from '@/components/Navigation';
import AuthGuard from '@/components/auth/AuthGuard';
import { predictionsAPI } from '@/lib/api';
import { IrrigationSchedule } from '@/types/predictions';
import { toast } from 'react-hot-toast';

export default function SchedulesPage() {
  const [schedules, setSchedules] = useState<IrrigationSchedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  useEffect(() => {
    loadSchedules();
  }, [filter]);

  const loadSchedules = async () => {
    try {
      setLoading(true);
      let data;
      if (filter === 'pending') {
        data = await predictionsAPI.getPendingSchedules();
      } else if (filter === 'overdue') {
        data = await predictionsAPI.getOverdueSchedules();
      } else {
        const params = filter !== 'all' ? { status: filter } : {};
        data = await predictionsAPI.getSchedules(params);
      }
      setSchedules(Array.isArray(data) ? data : data.results || []);
    } catch (err) {
      console.error('Failed to load schedules:', err);
      toast.error('Failed to load schedules');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (id: number) => {
    setActionLoading(id);
    try {
      await predictionsAPI.confirmSchedule(id);
      toast.success('Schedule confirmed!');
      loadSchedules();
    } catch (err) {
      console.error('Failed to confirm schedule:', err);
      toast.error('Failed to confirm schedule');
    } finally {
      setActionLoading(null);
    }
  };

  const handleSkip = async (id: number) => {
    setActionLoading(id);
    try {
      await predictionsAPI.skipSchedule(id);
      toast.success('Schedule skipped');
      loadSchedules();
    } catch (err) {
      console.error('Failed to skip schedule:', err);
      toast.error('Failed to skip schedule');
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { bg: string; text: string; label: string }> = {
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Pending' },
      confirmed: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Confirmed' },
      completed: { bg: 'bg-green-100', text: 'text-green-800', label: 'Completed' },
      skipped: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Skipped' },
      overdue: { bg: 'bg-red-100', text: 'text-red-800', label: 'Overdue' },
    };
    const config = statusConfig[status] || statusConfig.pending;
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const priorityConfig: Record<string, { bg: string; text: string; label: string }> = {
      critical: { bg: 'bg-red-100', text: 'text-red-800', label: 'Critical' },
      high: { bg: 'bg-orange-100', text: 'text-orange-800', label: 'High' },
      medium: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Medium' },
      low: { bg: 'bg-green-100', text: 'text-green-800', label: 'Low' },
    };
    const config = priorityConfig[priority] || priorityConfig.medium;
    return (
      <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        <Navigation currentPage="schedules" />

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Breadcrumb */}
          <nav className="flex mb-6" aria-label="Breadcrumb">
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
                  <span className="ml-4 text-sm font-medium text-gray-500">Schedules</span>
                </div>
              </li>
            </ol>
          </nav>

          {/* Header */}
          <div className="md:flex md:items-center md:justify-between mb-8">
            <div className="flex-1 min-w-0">
              <h1 className="text-3xl font-bold text-gray-900">Irrigation Schedules</h1>
              <p className="mt-2 text-lg text-gray-600">
                View and manage your irrigation schedules
              </p>
            </div>
          </div>

          {/* Filters */}
          <div className="bg-white rounded-xl shadow p-4 mb-6">
            <div className="flex flex-wrap gap-2">
              {[
                { value: 'all', label: 'All Schedules' },
                { value: 'pending', label: 'Pending' },
                { value: 'confirmed', label: 'Confirmed' },
                { value: 'completed', label: 'Completed' },
                { value: 'overdue', label: 'Overdue' },
                { value: 'skipped', label: 'Skipped' },
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => setFilter(option.value)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filter === option.value
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {/* Loading */}
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-green-600"></div>
              <span className="ml-4 text-lg text-gray-600">Loading schedules...</span>
            </div>
          )}

          {/* Empty State */}
          {!loading && schedules.length === 0 && (
            <div className="text-center py-12 bg-white rounded-xl shadow">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h3 className="mt-4 text-lg font-medium text-gray-900">No schedules found</h3>
              <p className="mt-2 text-gray-600">
                {filter !== 'all' 
                  ? `No ${filter} schedules. Try a different filter.`
                  : 'Create schedules from the dashboard recommendations.'}
              </p>
              <Link
                href="/dashboard"
                className="mt-4 inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Go to Dashboard
              </Link>
            </div>
          )}

          {/* Schedules List */}
          {!loading && schedules.length > 0 && (
            <div className="space-y-4">
              {schedules.map((schedule) => (
                <div
                  key={schedule.id}
                  className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
                >
                  <div className="p-6">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                      {/* Left side - Field info */}
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-bold text-gray-900">{schedule.field_name}</h3>
                          {getStatusBadge(schedule.status)}
                          {getPriorityBadge(schedule.priority_level)}
                        </div>
                        <p className="text-gray-600 mb-3">{schedule.irrigation_reason}</p>
                        
                        {/* Schedule details */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">Date:</span>
                            <span className="ml-2 font-medium text-gray-900">
                              {new Date(schedule.recommended_date).toLocaleDateString('en-US', {
                                weekday: 'short',
                                month: 'short',
                                day: 'numeric'
                              })}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500">Time:</span>
                            <span className="ml-2 font-medium text-gray-900">
                              {schedule.recommended_time.slice(0, 5)}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500">Water:</span>
                            <span className="ml-2 font-medium text-gray-900">
                              {schedule.predicted_water_amount} L/m²
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-500">Confidence:</span>
                            <span className="ml-2 font-medium text-gray-900">
                              {Math.round(parseFloat(String(schedule.confidence_score)) * 100)}%
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Right side - Actions */}
                      <div className="flex flex-col sm:flex-row gap-2">
                        {schedule.status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleConfirm(schedule.id)}
                              disabled={actionLoading === schedule.id}
                              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 font-medium"
                            >
                              {actionLoading === schedule.id ? 'Loading...' : 'Confirm'}
                            </button>
                            <button
                              onClick={() => handleSkip(schedule.id)}
                              disabled={actionLoading === schedule.id}
                              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50 font-medium"
                            >
                              Skip
                            </button>
                          </>
                        )}
                        <Link
                          href={`/fields/${schedule.field}`}
                          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-center font-medium"
                        >
                          View Field
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </AuthGuard>
  );
}
