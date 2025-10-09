import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AuthGuard from '@/components/auth/AuthGuard';
import { api } from '@/lib/api';
import { ChangePasswordData } from '@/types/auth';

export default function Profile() {
  const { user, logout, refreshUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Edit profile form
  const [editData, setEditData] = useState({
    name: user?.name || '',
    location: user?.location || '',
  });

  // Change password form
  const [passwordData, setPasswordData] = useState<ChangePasswordData>({
    old_password: '',
    password: '',
    password2: '',
  });

  const handleEditChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEditData({ ...editData, [e.target.name]: e.target.value });
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPasswordData({ ...passwordData, [e.target.name]: e.target.value });
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');

    try {
      await api.patch('/auth/user/', editData);
      await refreshUser();
      setMessage('Profile updated successfully');
      setIsEditing(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (passwordData.password !== passwordData.password2) {
      setError('New passwords do not match');
      return;
    }

    if (passwordData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    try {
      await api.put('/auth/change-password/', passwordData);
      setMessage('Password changed successfully');
      setIsChangingPassword(false);
      setPasswordData({ old_password: '', password: '', password2: '' });
    } catch (err: any) {
      const errorData = err.response?.data;
      if (errorData) {
        const firstError = Object.values(errorData)[0];
        setError(Array.isArray(firstError) ? firstError[0] : String(firstError));
      } else {
        setError('Failed to change password');
      }
    }
  };

  return (
    <AuthGuard>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-primary-700">🌱 My Profile</h1>
            <button
              onClick={logout}
              className="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-5xl mx-auto px-4 py-8">
          {message && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg">
              {message}
            </div>
          )}

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
              {error}
            </div>
          )}

          {/* Profile Information */}
          <div className="card mb-6">
            <div className="flex justify-between items-start mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Profile Information</h2>
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-4 py-2 text-sm btn-secondary"
                >
                  Edit Profile
                </button>
              )}
            </div>

            {!isEditing ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Name</label>
                  <p className="text-gray-900">{user?.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Email</label>
                  <p className="text-gray-900">{user?.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Location</label>
                  <p className="text-gray-900">{user?.location || 'Not set'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Member Since</label>
                  <p className="text-gray-900">
                    {user?.date_joined ? new Date(user.date_joined).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
              </div>
            ) : (
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                    Name
                  </label>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    required
                    value={editData.name}
                    onChange={handleEditChange}
                    className="input-field"
                  />
                </div>
                <div>
                  <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
                    Location
                  </label>
                  <input
                    id="location"
                    name="location"
                    type="text"
                    value={editData.location}
                    onChange={handleEditChange}
                    className="input-field"
                  />
                </div>
                <div className="flex gap-3">
                  <button type="submit" className="btn-primary">
                    Save Changes
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setIsEditing(false);
                      setEditData({ name: user?.name || '', location: user?.location || '' });
                    }}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>

          {/* Change Password */}
          <div className="card">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Change Password</h2>
                <p className="text-sm text-gray-600 mt-1">Update your password to keep your account secure</p>
              </div>
              {!isChangingPassword && (
                <button
                  onClick={() => setIsChangingPassword(true)}
                  className="px-4 py-2 text-sm btn-secondary"
                >
                  Change Password
                </button>
              )}
            </div>

            {isChangingPassword && (
              <form onSubmit={handleChangePassword} className="space-y-4">
                <div>
                  <label htmlFor="old_password" className="block text-sm font-medium text-gray-700 mb-2">
                    Current Password
                  </label>
                  <input
                    id="old_password"
                    name="old_password"
                    type="password"
                    required
                    value={passwordData.old_password}
                    onChange={handlePasswordChange}
                    className="input-field"
                  />
                </div>
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                    New Password
                  </label>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    required
                    value={passwordData.password}
                    onChange={handlePasswordChange}
                    className="input-field"
                    placeholder="At least 8 characters"
                  />
                </div>
                <div>
                  <label htmlFor="password2" className="block text-sm font-medium text-gray-700 mb-2">
                    Confirm New Password
                  </label>
                  <input
                    id="password2"
                    name="password2"
                    type="password"
                    required
                    value={passwordData.password2}
                    onChange={handlePasswordChange}
                    className="input-field"
                  />
                </div>
                <div className="flex gap-3">
                  <button type="submit" className="btn-primary">
                    Update Password
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setIsChangingPassword(false);
                      setPasswordData({ old_password: '', password: '', password2: '' });
                    }}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
