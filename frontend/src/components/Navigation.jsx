import React, { useState } from 'react';

const Navigation = ({ user, onLogout }) => {
  return (
    <nav>
      <a href="#home" style={{ fontWeight: 'bold', marginRight: '2rem' }}>🏏 Box Cricket</a>
      <a href="#venues">Venues</a>
      {user && (
        <>
          <a href="#bookings">My Bookings</a>
          <a href="#profile">Profile</a>
          <button 
            onClick={onLogout}
            style={{
              background: 'rgba(255,255,255,0.2)',
              border: 'none',
              color: 'white',
              padding: '0.5rem 1rem',
              borderRadius: '4px',
              cursor: 'pointer',
              marginLeft: 'auto'
            }}
          >
            Logout
          </button>
        </>
      )}
      {!user && (
        <>
          <a href="#signup" style={{ marginLeft: 'auto' }}>Sign Up</a>
          <a href="#login">Login</a>
        </>
      )}
    </nav>
  );
};

export default Navigation;
