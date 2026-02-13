import React, { useState } from 'react';

const HomePage = ({ user, onLogout }) => {
  return (
    <div>
      <header className="hero">
        <div className="hero-inner container">
          <div className="hero-text">
            <h1>Book Box Cricket Courts Quickly</h1>
            <p>Find nearby venues, pick a court and time slot, and confirm your booking in seconds.</p>
            {user ? (
              <div className="hero-cta">
                <a className="btn" href="#booking">Book Now</a>
                <a className="btn btn-outline" href="#bookings">My Bookings</a>
              </div>
            ) : (
              <div className="hero-cta">
                <a className="btn" href="#signup">Get Started</a>
                <a className="btn btn-outline" href="#login">Login</a>
              </div>
            )}
          </div>
          <div className="hero-visual">
            <div className="court-illustration">🏏</div>
          </div>
        </div>
      </header>

      <section className="features container">
        <h2>How it works</h2>
        <div className="feature-grid">
          <div className="feature">
            <h3>🔍 Search Venues</h3>
            <p>Browse venues and available courts near you with real-time pricing and ratings.</p>
          </div>
          <div className="feature">
            <h3>📅 Select Time</h3>
            <p>Choose an available slot that fits your schedule with instant availability check.</p>
          </div>
          <div className="feature">
            <h3>✅ Confirm & Play</h3>
            <p>Complete booking, receive confirmation, and turn up to play your match.</p>
          </div>
        </div>
      </section>

      <section className="features container" style={{ backgroundColor: '#f9f9f9', padding: '3rem 2rem' }}>
        <h2>Why Choose Us?</h2>
        <div className="feature-grid">
          <div className="feature">
            <h3>🎯 Best Venues</h3>
            <p>Premium cricket courts with world-class facilities and equipment.</p>
          </div>
          <div className="feature">
            <h3>💰 Competitive Pricing</h3>
            <p>Transparent pricing with no hidden charges and flexible booking options.</p>
          </div>
          <div className="feature">
            <h3>⭐ Trusted Reviews</h3>
            <p>Read authentic reviews from other cricket enthusiasts to make informed decisions.</p>
          </div>
          <div className="feature">
            <h3>🚀 Instant Booking</h3>
            <p>One-click booking with instant confirmation and easy cancellation policy.</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
