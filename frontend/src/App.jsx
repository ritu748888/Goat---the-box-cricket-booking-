import React, { useState, useEffect } from 'react';
import Navigation from './components/Navigation';
import HomePage from './components/HomePage';
import VenuesList from './components/VenuesList';
import LoginPage from './components/LoginPage';
import MyBookings from './components/MyBookings';

const App = () => {
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('home');

  useEffect(() => {
    // Check if user is already logged in
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }

    // Handle hash-based routing
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1) || 'home';
      setCurrentPage(hash);
    };

    window.addEventListener('hashchange', handleHashChange);
    handleHashChange();

    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleLoginSuccess = () => {
    const storedUser = JSON.parse(localStorage.getItem('user'));
    setUser(storedUser);
    window.location.hash = '#venues';
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('user_id');
    localStorage.removeItem('auth_token');
    setUser(null);
    window.location.hash = '#home';
  };

  return (
    <div>
      <Navigation user={user} onLogout={handleLogout} />
      
      {currentPage === 'home' && <HomePage user={user} onLogout={handleLogout} />}
      {currentPage === 'venues' && <VenuesList />}
      {currentPage === 'login' && !user && <LoginPage onLoginSuccess={handleLoginSuccess} />}
      {currentPage === 'bookings' && user && <MyBookings />}
      
      {currentPage === 'signup' && (
        <div className="container" style={{ maxWidth: '400px', marginTop: '50px' }}>
          <h2>Sign Up</h2>
          <p style={{ textAlign: 'center', color: '#666' }}>
            Sign up functionality coming soon! Use the demo account:
          </p>
          <p style={{ textAlign: 'center' }}>
            <strong>Email:</strong> admin@test.com<br />
            <strong>Password:</strong> admin123
          </p>
          <button className="btn" onClick={() => window.location.hash = '#login'} style={{ width: '100%' }}>
            Go to Login
          </button>
        </div>
      )}

      {currentPage === 'profile' && user && (
        <div className="container">
          <div className="card" style={{ maxWidth: '600px', margin: '2rem auto' }}>
            <h2>User Profile</h2>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>Phone:</strong> {user.phone || 'Not provided'}</p>
            <p><strong>Member since:</strong> {new Date(user.date_joined).toLocaleDateString()}</p>
            <div className="card-footer">
              <button className="btn btn-secondary" onClick={() => window.location.hash = '#bookings'}>
                View My Bookings
              </button>
            </div>
          </div>
        </div>
      )}

      <footer style={{ backgroundColor: '#212121', color: 'white', textAlign: 'center', padding: '2rem', marginTop: '4rem' }}>
        <p>&copy; 2026 Box Cricket Booking. All rights reserved.</p>
        <p>Built with Django REST Framework & React</p>
      </footer>
    </div>
  );
};

export default App;
