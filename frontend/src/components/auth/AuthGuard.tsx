import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/contexts/AuthContext';

interface AuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
}

export default function AuthGuard({ children, requireAuth = true }: AuthGuardProps) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (requireAuth && !user) {
        // Redirect to login if auth is required but user is not logged in
        router.push('/login');
      } else if (!requireAuth && user) {
        // Redirect to dashboard if user is already logged in (e.g., on login/register pages)
        router.push('/dashboard');
      }
    }
  }, [user, loading, requireAuth, router]);

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If requireAuth and no user, show nothing (will redirect)
  if (requireAuth && !user) {
    return null;
  }

  // If !requireAuth and user exists, show nothing (will redirect)
  if (!requireAuth && user) {
    return null;
  }

  return <>{children}</>;
}
