import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { FiMessageSquare } from "react-icons/fi";
import { CiSearch } from "react-icons/ci";
import { CiHeart } from "react-icons/ci";
import { IoIosNotificationsOutline } from "react-icons/io";
import { getCookie, removeCookie } from "../utils/cookies";

const Header = () => {
  const navigate = useNavigate();
  const token = getCookie("access_token");
  const isLoggedIn = !!token;

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

  const GuestHeader = (
    <div className="guest-header">
      <div className="website-title">
        <img className="logo" src="./dz-kitablogo.png" alt="logo" />
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
        {/* <button
          onClick={() => navigate("/wishlist")}
          className="wishlist-icon-btn"
          style={{
            background: "none",
            border: "none",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            height: "30px",
            width: "30px",
            padding: 0,
          }}
        >
          <CiHeart size={28} />
        </button> */}
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
        <img className="logo" src="./dz-kitablogo.png" alt="logo" />
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
        <a href="#about">About us</a>
        <a href="#contact">Contact us</a>
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
          <Link to="/notifications">
            <IoIosNotificationsOutline className="icon" />
          </Link>
        </div>
        <div className="user" onClick={handleLogout} style={{ cursor: 'pointer' }} title="Click to Logout">
          {(() => {
            try {
              const user = getCookie('user');
              return user ? JSON.parse(user).username?.charAt(0).toUpperCase() : 'U';
            } catch (e) {
              return 'U';
            }
          })()}
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

