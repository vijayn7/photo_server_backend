import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import styled from 'styled-components';
import Login from './components/Login';
import Register from './components/Register';
import AdminDashboard from './components/AdminDashboard';
import UserDashboard from './components/UserDashboard';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

const AppContainer = styled.div`
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  margin: 0;
  padding: 0;
  background-color: #121212;
  color: #e0e0e0;
  min-height: 100vh;
`;

function ProtectedRoute({ children, requireAdmin = false }) {
  const { user, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (requireAdmin && !user?.is_admin) {
    return <Navigate to="/dashboard" />;
  }
  
  return children;
}

function AppRoutes() {
  const { user, isAuthenticated } = useAuth();
  
  return (
    <Routes>
      <Route path="/login" element={
        isAuthenticated ? 
          <Navigate to={user?.is_admin ? "/admin" : "/dashboard"} /> : 
          <Login />
      } />
      <Route path="/register" element={
        isAuthenticated ? 
          <Navigate to={user?.is_admin ? "/admin" : "/dashboard"} /> : 
          <Register />
      } />
      <Route path="/admin" element={
        <ProtectedRoute requireAdmin={true}>
          <AdminDashboard />
        </ProtectedRoute>
      } />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <UserDashboard />
        </ProtectedRoute>
      } />
      <Route path="/" element={
        <Navigate to={isAuthenticated ? (user?.is_admin ? "/admin" : "/dashboard") : "/login"} />
      } />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContainer>
          <AppRoutes />
        </AppContainer>
      </Router>
    </AuthProvider>
  );
}

export default App;
