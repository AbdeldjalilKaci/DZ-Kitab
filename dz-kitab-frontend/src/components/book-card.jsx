import React from "react";
import { CiHeart } from "react-icons/ci";
import { FaHeart } from "react-icons/fa";
import { useWishlist } from "../context/WishlistContext";

export const BookCard = ({ id, img, title, desc, price, buy_func }) => {
  const { isInWishlist, toggleWishlist } = useWishlist();
  const isWishlisted = isInWishlist(id);

  return (
    <div className="card-book" style={{ position: "relative" ,background: "linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)",}}>
      <button
        onClick={(e) => {
          e.stopPropagation();
          toggleWishlist(id);
        }}
        style={{
          position: "absolute",
          top: "10px",
          right: "10px",
          background: "white",
          border: "none",
          borderRadius: "50%",
          width: "30px",
          height: "30px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          cursor: "pointer",
          zIndex: 10,
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
        }}
      >
        {isWishlisted ? (
          <FaHeart size={18} color="red" />
        ) : (
          <CiHeart size={20} color="black" />
        )}
      </button>
      <div className="book-cover">
        <img className="book-img" src={img} alt="" />
      </div>
      <h4>{title}</h4>
      <p className="book-desc">{desc}</p>
      <hr></hr>
      <div className="buy-book">
        <p>{price}</p>
        <button className="buy-button" onClick={buy_func}>
          Buy Now
        </button>
      </div>
    </div>
  );
};
