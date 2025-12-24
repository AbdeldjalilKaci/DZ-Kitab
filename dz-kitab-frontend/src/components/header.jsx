import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { FiMessageSquare } from "react-icons/fi";
import { CiSearch } from "react-icons/ci";
import { CiHeart } from "react-icons/ci";
import { IoIosNotificationsOutline } from "react-icons/io";
const Header = () => {
  const navigate = useNavigate();
  const nagigate_to_login_page = () => {
    navigate("/login");
  };
  const nagigate_to_register_page = () => {
    navigate("/register");
  };
  return (
    <header>
      <div className="guest-header">
        <div className="website-title">
          <img className="logo" src="./dz-kitablogo.png"></img>
          <a href="/" className=" a">
            <h3 className="">
              <span className="  ">DZ</span>-KITAB
            </h3>
          </a>
        </div>
        <div className="links">
          <a href="/addannounce">Home</a>
          <a href="/catalog">Catalog</a>
          <a href="#about">About us</a>
          <a href="#contact">Contact us</a>
        </div>
        <div className="buttons">
          <button
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
          </button>
          <button onClick={nagigate_to_login_page} className="login-button">
            Login
          </button>
          <button
            onClick={nagigate_to_register_page}
            className="register-button"
          >
            Register
          </button>
        </div>
      </div>

      {/* <div className="user-header">
                <div className="website-title">
                    <img className='logo' src='./dz-kitablogo.png'></img>
                    <a className="a"><h3><span>DZ</span>-KITAB</h3></a>
                </div>
                <div className="links">
                    <a>Home</a>
                    <a>Books</a>
                    <a>About us</a>
                    <a>Contact us</a>
                </div>

                <div className="user-links">
                    <div className="icons-link">
                        <a><CiSearch className='icon' /></a>
                        <a><FiMessageSquare className='icon' /></a>
                        <a><CiHeart className='icon' /></a>
                        <a><IoIosNotificationsOutline className='icon' /></a>
                    </div>
                    <div className="user">
                        A
                    </div>

                </div>
            </div> */}
    </header>
  );
};

export default Header;
