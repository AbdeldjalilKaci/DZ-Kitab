import React, { useState } from 'react';
import { Link, useNavigate } from "react-router-dom";
import { MdHome, MdDashboard, MdPeople, MdAnnouncement } from "react-icons/md";
import { FiMessageSquare } from "react-icons/fi"; // Matching Header icons style if needed, though Admin usually has specific ones
import { CiSearch } from "react-icons/ci";
import { IoIosNotificationsOutline } from "react-icons/io";

// Reusing global header styles which seem to be in index.css (based on class names like "user-header")

function NavAdmin() {
  const navigate = useNavigate();
  // Mock Admin User
  const [user] = useState({ name: "Admin", role: "Administrator" });
  const [showDropdown, setShowDropdown] = useState(false);

  // Admin Logout Logic
  const handleLogout = () => {
    // Implement admin logout or redirect
    navigate("/");
  };

  return (
    <header>
      <div className="user-header">
        {/* --- Logo Area --- */}
        <div className="website-title">
          <img className="logo" src="/dz-kitablogo.png" alt="logo" />
          <Link to="/" className="a">
            <h3>
              <span>DZ</span>-KITAB
              <span style={{ fontSize: '10px', marginLeft: '5px', background: '#F3A109', color: 'white', padding: '2px 6px', borderRadius: '4px', verticalAlign: 'middle' }}>ADMIN</span>
            </h3>
          </Link>
        </div>

        {/* --- Admin Navigation Links --- */}
        <div className="links">
          <Link to="/DashboardAdmin">Dashboard</Link>
          <Link to="/UsersAdmin">Users</Link>
          <Link to="/AnnouncementsAdmin">Announcements</Link>
        </div>

        {/* --- Right Side: Standard User Header Icons + Admin Profile --- */}
        <div className="user-links">
          <div className="icons-link">
            {/* Useful links for Admin to jump back */}
            <Link to="/" title="Public Site">
              <MdHome className="icon" />
            </Link>
          </div>

          {/* Admin Profile Dropdown (Matching Header.jsx structure) */}
          <div style={{ position: 'relative' }}>
            <div
              className="user"
              onClick={() => setShowDropdown(!showDropdown)}
              style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}
              title="Admin Menu"
            >
              <div style={{ width: '30px', height: '30px', borderRadius: '50%',  color: 'white', display: 'flex', justifyContent: 'center', alignItems: 'center', fontWeight: 'bold' }}>
                {user.name[0]}
              </div>
            </div>

            {showDropdown && (
              <div style={{
                position: 'absolute',
                top: '120%',
                right: 0,
                backgroundColor: 'white',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                borderRadius: '8px',
                padding: '8px 0',
                zIndex: 1000,
                minWidth: '200px',
                border: '1px solid #eee'
              }}>
                <div
                  onClick={() => { navigate('/DashboardAdmin'); setShowDropdown(false); }}
                  style={{ padding: '10px 16px', cursor: 'pointer', fontSize: '14px', color: '#333', transition: 'background 0.2s' }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#f5f5f5'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}
                >
                  Dashboard
                </div>
                <div style={{ height: '1px', backgroundColor: '#eee', margin: '4px 0' }}></div>
                <div
                  onClick={() => { handleLogout(); setShowDropdown(false); }}
                  style={{ padding: '10px 16px', cursor: 'pointer', fontSize: '14px', color: '#e53e3e', transition: 'background 0.2s' }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#fff5f5'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}
                >
                  Log Out
                </div>
              </div>
            )}
          </div>

        </div>
      </div>
    </header>
  );
}

export default NavAdmin;