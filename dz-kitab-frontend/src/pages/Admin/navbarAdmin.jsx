
import React, { useState, useEffect, useRef } from 'react'
import { Link} from "react-router-dom";


function NavAdmin() {
 
  const [user] = useState({ name: "Ahmed", profilePic: "" });

  return (
    <div className="guest-header">
     <div className="website-title flex items-center gap-2">
  <img className="logo" src="./dz-kitablogo.png" alt="Logo" />
  <Link to="/" className="no-underline">
    <h3 className="font-bold text-lg">
      <span className="text-[#F3A109]">DZ</span>
      <span className="text-black">-KITAB</span>
    </h3>
  </Link>
</div>

     <div className="links flex gap-5">
  <Link to="/">Home</Link>
  <Link to="/UsersAdmin">Users management</Link>
  <Link to="/AnnouncementsAdmin">Announcements management</Link>
  <Link to="/DashboardAdmin">Dashboard</Link>
</div>

     
        <Link to="/dashboard">
  <div className="w-9 h-9 rounded-full overflow-hidden cursor-pointer">
    {user?.profilePic ? (
      <img
        src={user.profilePic}
        alt="User"
        className="w-full h-full object-cover"
      />
    ) : (
      <div className="w-full h-full bg-[#F3A109] text-white flex items-center justify-center font-semibold">
        {user?.name ? user.name[0].toUpperCase() : "U"}
      </div>
    )}
  </div>
</Link>
     
    </div>
  );
}

export default NavAdmin