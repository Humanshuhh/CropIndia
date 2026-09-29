// PROTOTYPE ONLY – production should use Firebase custom claims + server‑side verification
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface RequireRoleProps {
  requiredRole: 'admin' | 'farmer';
  children: React.ReactNode;
}

export const RequireRole: React.FC<RequireRoleProps> = ({ requiredRole, children }) => {
  const { user, role, roleLoading } = useAuth();

  // While role is loading, avoid flashing UI – render nothing or a simple placeholder
  if (roleLoading) {
    return null;
  }

  if (!user) {
    // Redirect users to the login page for their required role
    return (
      <Navigate
        to={requiredRole === 'admin' ? '/admin/login' : '/login'}
        replace
      />
    );
  }

  if (role !== requiredRole) {
    // Wrong role – redirect to home (no toast as per spec)
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

