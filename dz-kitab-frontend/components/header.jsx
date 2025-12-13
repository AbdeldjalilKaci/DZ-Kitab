import React from "react";
import { Link } from "react-router-dom";
import { FiMessageSquare } from "react-icons/fi";
import { CiSearch } from "react-icons/ci";
import { CiHeart } from "react-icons/ci";
import { IoIosNotificationsOutline } from "react-icons/io";
const Header = () => {
  return (
    <header>
      <div className="guest-header">
        <div className="website-title">
          <img className="logo" src="./dz-kitablogo.png"></img>
          <a className="a">
            <h3>
              <span>DZ</span>-KITAB
            </h3>
          </a>
        </div>
        <div className="links">
          <a>Home</a>
          <a>About us</a>
          <a>Contact us</a>
        </div>
        <div className="buttons">
          <Link to="/login">
            <button className="login-button">Login</button>
          </Link>
          <button className="register-button">Register</button>
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
