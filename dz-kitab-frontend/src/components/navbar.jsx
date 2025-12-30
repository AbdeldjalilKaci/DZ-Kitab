import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { CiHeart } from "react-icons/ci";
import { FaRegCommentDots, FaBell } from "react-icons/fa";

const Navbar = () => {
  const navigate = useNavigate();

  // MOCK user en attendant backend
  const [user, setUser] = useState({
    name: "Ahmed",
    profilePic: "", // si vide, on affichera l’initiale
  });

  return (
    <header>
      <div className="guest-header">
        <div className="website-title">
          <img className="logo" src="./dz-kitablogo.png" alt="Logo" />
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

        <div className="buttons flex items-center hover:text-[#F3A109] gap-4">
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

        <div className="flex items-center gap-5">
  {/* 💬 Messagerie */}
  <button
    onClick={() => navigate("/messages")}
    className="text-black hover:text-[#F3A109] transition-colors duration-200"
  >
    <FaRegCommentDots size={22} />
  </button>

  {/* 🔔 Notifications */}
  <button
    onClick={() => navigate("/notifications")}
    className="text-black hover:text-[#F3A109] transition-colors duration-200"
  >
    <FaBell size={22} />
  </button>

  {/* 👤 Photo / Initiale utilisateur */}
  <div className="w-9 h-9 rounded-full overflow-hidden cursor-pointer">
    {user?.profilePic ? (
      <img
        src={user.profilePic}
        alt="User Photo"
        className="w-full h-full object-cover"
      />
    ) : (
      <div className="w-full h-full bg-[#F3A109] text-white flex items-center justify-center font-semibold">
        {user?.name ? user.name[0].toUpperCase() : "U"}
      </div>
    )}
  </div>
</div>

        </div>
      </div>
    </header>
  );
};

export default Navbar;
