import React, { createContext, useState, useEffect, useContext } from "react";
import api from "../utils/api";
import { getCookie } from "../utils/cookies";

const WishlistContext = createContext();

export const useWishlist = () => useContext(WishlistContext);

export const WishlistProvider = ({ children }) => {
  const [wishlist, setWishlist] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchWishlist = async () => {
    const token = getCookie('access_token');

    if (!token) {
      setWishlist([]);
      return;
    }

    try {
      setLoading(true);
      const response = await api.get('/api/wishlist');
      const ids = response.data.items.map(item => item.announcement_id);
      setWishlist(ids);
    } catch (error) {
      console.error("Error fetching wishlist:", error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch wishlist from backend on mount
  useEffect(() => {
    fetchWishlist();
  }, []);

  const addToWishlist = async (bookId) => {
    const token = getCookie('access_token');

    if (!token) {
      alert("Please login to use the wishlist");
      return;
    }

    try {
      await api.post('/api/wishlist/', { announcement_id: bookId });
      setWishlist((prev) => {
        if (!prev.includes(bookId)) {
          return [...prev, bookId];
        }
        return prev;
      });
    } catch (error) {
      console.error("Error adding to wishlist:", error);
    }
  };

  const removeFromWishlist = async (bookId) => {
    try {
      await api.delete(`/api/wishlist/${bookId}`);
      setWishlist((prev) => prev.filter((id) => id !== bookId));
    } catch (error) {
      console.error("Error removing from wishlist:", error);
    }
  };

  const isInWishlist = (bookId) => {
    return wishlist.includes(bookId);
  };

  const toggleWishlist = (bookId) => {
    if (isInWishlist(bookId)) {
      removeFromWishlist(bookId);
    } else {
      addToWishlist(bookId);
    }
  };

  return (
    <WishlistContext.Provider
      value={{
        wishlist,
        addToWishlist,
        removeFromWishlist,
        isInWishlist,
        toggleWishlist,
        fetchWishlist,
        loading

      }}
    >
      {children}
    </WishlistContext.Provider>
  );
};

