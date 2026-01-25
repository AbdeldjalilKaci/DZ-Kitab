import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { FiMessageSquare } from "react-icons/fi";
import { CiSearch } from "react-icons/ci";
import { CiHeart } from "react-icons/ci";
import { IoIosNotificationsOutline } from "react-icons/io";
import { getCookie, removeCookie } from "../utils/cookies";

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation(); // To check current path
  const token = getCookie("access_token");
  const isLoggedIn = !!token;
  const [user, setUser] = useState(null);
  const [isbnSearch, setIsbnSearch] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0); // NEW: Unread count state

  const fetchUnreadCount = async () => {
    if (!token) return;
    try {
      const res = await api.get("/api/notifications/unread-count");
      setUnreadCount(res.data.unread_count || 0);
    } catch (e) {
      console.error("Error fetching unread count", e);
    }
  };

  useEffect(() => {
    try {
      const userData = getCookie("user");
      if (userData) {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        fetchUnreadCount(); // Initial fetch
      }
    } catch (e) {
      console.error("Error parsing user cookie", e);
    }

    // Polling interval (30 seconds)
    const interval = setInterval(() => {
      if (token) fetchUnreadCount();
    }, 30000);

    return () => clearInterval(interval);
  }, [token]);

  const handleLogout = () => {
    removeCookie("access_token");
    removeCookie("user");
    navigate("/");
  };


  const nagigate_to_login_page = () => {
    navigate("/login");
  };
  const nagigate_to_register_page = () => {
    navigate("/register");
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (isbnSearch.trim()) {
      // Navigate to catalog with search query, or specialized search
      // For now, let's assume we want to filter catalog
      navigate(`/catalog?search=${isbnSearch}`);
      // OR if strictly "search in books with isbn", maybe go to addannounce? 
      // "add search in books with isbn" usually means for BUYING.
      // So Catalog is correct.
    }
  };

  // Check if we are on an admin page or dashboard that has its own layout
  // User request: "if there is deplicate navbar hidd the header"
  // Assuming /DashboardAdmin and /dashboard might have sidebars.
  // Let's hide this global header on those specific paths if they are fully separate layouts.
  // However, usually Dashboard still needs a header. Admin Dashboard definitely has its own.
  // Check if we are on an admin page or dashboard that has its own layout
  // User request: "if there is deplicate navbar hidd the header"
  // Assuming /DashboardAdmin and /dashboard might have sidebars.
  // Let's hide this global header on those specific paths if they are fully separate layouts.
  // However, usually Dashboard still needs a header. Admin Dashboard definitely has its own.
  const isAdminComp = location.pathname.toLowerCase().includes('admin');

  // If we want to hide header on admin pages:
  if (isAdminComp) {
    return null;
  }

  const GuestHeader = (
    <div className="guest-header">
      <div className="website-title">
        <img className="logo" src="/dz-kitablogo.png" alt="logo" />
        <Link to="/" className="a">
          <h3>
            <span>DZ</span>-KITAB
          </h3>
        </Link>
      </div>



      <div className="links">
        <Link to="/">Home</Link>
        <Link to="/catalog">Books</Link>
        <a href="#about">About us</a>
        <a href="#contact">Contact us</a>
      </div>
      <div className="buttons">
        <button onClick={nagigate_to_login_page} className="login-button">
          Login
        </button>
        <button onClick={nagigate_to_register_page} className="register-button">
          Register
        </button>
      </div>
    </div>
  );

  const UserHeader = (
    <div className="user-header">
      <div className="website-title">
        <img className="logo" src="/dz-kitablogo.png" alt="logo" />
        <Link to="/" className="a">
          <h3>
            <span>DZ</span>-KITAB
          </h3>
        </Link>
      </div>



      <div className="links">
        <Link to="/">Home</Link>
        <Link to="/catalog">Books</Link>
        <Link to="/addannounce">Add Announcement</Link>
        {/* Admin Link if role is admin */}
        {user && user.role === 'admin' && (
          <Link to="/DashboardAdmin" style={{ color: 'red', fontWeight: 'bold' }}>Admin</Link>
        )}
        {/* User Dashboard Link */}
        <Link to="/dashboard">Dashboard</Link>
      </div>

      <div className="user-links">
        <div className="icons-link">
          <Link to="/catalog">
            <CiSearch className="icon" />
          </Link>
          <Link to="/message">
            <FiMessageSquare className="icon" />
          </Link>
          <Link to="/wishlist">
            <CiHeart className="icon" />
          </Link>
          <Link to="/notifications" className="relative group">
            <IoIosNotificationsOutline className="icon" />
            {unreadCount > 0 && (
              <span className="notification-dot"></span>
            )}
          </Link>
        </div>
        <div style={{ position: 'relative' }}>
          <div
            className="user"
            onClick={() => setShowDropdown(!showDropdown)}
            style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}
            title="User Menu"
          >
            <div style={{ width: '30px', height: '30px', borderRadius: '50%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              {user ? user.username?.charAt(0).toUpperCase() : 'U'}
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
                onClick={() => { navigate('/dashboard'); setShowDropdown(false); }}
                style={{ padding: '10px 16px', cursor: 'pointer', fontSize: '14px', color: '#333', transition: 'background 0.2s' }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#f5f5f5'}
                onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}
              >
                Profile
              </div>
              <div
                onClick={() => { navigate('/myannouncements'); setShowDropdown(false); }}
                style={{ padding: '10px 16px', cursor: 'pointer', fontSize: '14px', color: '#333', transition: 'background 0.2s' }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#f5f5f5'}
                onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}
              >
                My Announcements
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
  );

  return (
    <header>
      {isLoggedIn ? UserHeader : GuestHeader}
    </header>
  );
};

export default Header;

