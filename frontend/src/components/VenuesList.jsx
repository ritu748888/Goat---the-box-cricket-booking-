import React, { useState, useEffect } from 'react';

const VenuesList = () => {
  const [venues, setVenues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedVenue, setSelectedVenue] = useState(null);

  useEffect(() => {
    fetchVenues();
  }, []);

  const fetchVenues = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/venues/');
      const data = await response.json();
      if (data.results) {
        setVenues(data.results);
      } else {
        setVenues(data);
      }
    } catch (err) {
      setError('Failed to load venues');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="container"><p>Loading venues...</p></div>;
  if (error) return <div className="container"><div className="alert alert-error">{error}</div></div>;

  return (
    <div className="container">
      <h2>Book Your Court</h2>
      <div className="venues-grid">
        {venues.map((venue) => (
          <div key={venue.id} className="venue-card">
            <div className="venue-image">🏏</div>
            <div className="venue-content">
              <h3 className="venue-name">{venue.name}</h3>
              <p className="venue-city">{venue.city}</p>
              <div className="venue-rating">
                <span className="stars">★★★★☆</span>
                <span>{venue.rating.toFixed(1)}/5.0</span>
              </div>
              <p className="venue-courts">
                {venue.courts_count || 0} courts available
              </p>
              <button className="btn btn-small" onClick={() => setSelectedVenue(venue)}>
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>

      {selectedVenue && (
        <div className="modal active">
          <div className="modal-content">
            <span className="modal-close" onClick={() => setSelectedVenue(null)}>&times;</span>
            <h2>{selectedVenue.name}</h2>
            <p><strong>Location:</strong> {selectedVenue.address}</p>
            <p><strong>City:</strong> {selectedVenue.city}</p>
            <p><strong>Phone:</strong> {selectedVenue.phone}</p>
            <p><strong>Description:</strong> {selectedVenue.description}</p>
            <div className="card-footer">
              <button className="btn" onClick={() => alert('Book a court from here!')}>
                Book Court
              </button>
              <button className="btn btn-secondary" onClick={() => setSelectedVenue(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VenuesList;
