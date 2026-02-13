import React, { useState, useEffect } from 'react';

const MyBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('upcoming');

  useEffect(() => {
    fetchBookings();
  }, [activeTab]);

  const fetchBookings = async () => {
    try {
      const endpoint = activeTab === 'upcoming' 
        ? 'http://localhost:8000/api/bookings/upcoming/'
        : 'http://localhost:8000/api/bookings/past/';
      
      const response = await fetch(endpoint, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      });
      
      if (!response.ok && response.status === 401) {
        setError('Please log in to view bookings');
        return;
      }
      
      const data = await response.json();
      setBookings(Array.isArray(data) ? data : data.results || []);
    } catch (err) {
      setError('Failed to load bookings');
    } finally {
      setLoading(false);
    }
  };

  const cancelBooking = async (bookingId) => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) return;

    try {
      const response = await fetch(`http://localhost:8000/api/bookings/${bookingId}/cancel/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      });

      if (response.ok) {
        fetchBookings();
        alert('Booking cancelled successfully');
      }
    } catch (err) {
      alert('Failed to cancel booking');
    }
  };

  if (loading) return <div className="container"><p>Loading bookings...</p></div>;

  return (
    <div className="container">
      <h2>My Bookings</h2>
      
      <div style={{ marginBottom: '2rem', borderBottom: '2px solid #e0e0e0' }}>
        <button
          className={`btn ${activeTab === 'upcoming' ? '' : 'btn-secondary'}`}
          onClick={() => setActiveTab('upcoming')}
          style={{ marginRight: '1rem' }}
        >
          Upcoming
        </button>
        <button
          className={`btn ${activeTab === 'past' ? '' : 'btn-secondary'}`}
          onClick={() => setActiveTab('past')}
        >
          Past Bookings
        </button>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {bookings.length === 0 ? (
        <div className="card">
          <p style={{ textAlign: 'center', color: '#999' }}>No {activeTab} bookings found</p>
        </div>
      ) : (
        <div>
          {bookings.map((booking) => (
            <div key={booking.id} className="card">
              <div className="card-header">
                <h3>{booking.venue_name} - {booking.court_name}</h3>
              </div>
              <div className="card-body">
                <p><strong>Date:</strong> {booking.date}</p>
                <p><strong>Time:</strong> {booking.start_time} - {booking.end_time}</p>
                <p><strong>Players:</strong> {booking.number_of_players}</p>
                <p><strong>Price:</strong> ₹{booking.total_price}</p>
                <p><strong>Status:</strong> <span style={{ color: booking.status === 'confirmed' ? '#2e7d32' : '#c62828' }}>{booking.status.toUpperCase()}</span></p>
              </div>
              {activeTab === 'upcoming' && booking.status !== 'cancelled' && (
                <div className="card-footer">
                  <button className="btn btn-danger" onClick={() => cancelBooking(booking.id)}>
                    Cancel Booking
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyBookings;
