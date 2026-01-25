import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import NavAdmin from "./navbarAdmin";
import api from "../../utils/api";
import { FaTrash, FaEye } from "react-icons/fa";
import "../Listing.css"; // Reuse Catalog styles for exact match

const AnnouncementsAdmin = () => {
  const navigate = useNavigate();
  const [books, setBooks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedStatus, setSelectedStatus] = useState("");
  const [selectedDomains, setSelectedDomains] = useState([]);
  const [selectedPrice, setSelectedPrice] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("default");
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch ALL announcements for Admin
  useEffect(() => {
    const fetchAnnouncements = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch list of announcements (limit 100 for admin view)
        const response = await api.get('/api/books/announcements', {
          params: { limit: 100 }
        });

        if (response.data?.announcements) {
          setBooks(response.data.announcements);
        } else if (Array.isArray(response.data)) {
          setBooks(response.data);
        } else {
          setBooks([]);
        }
      } catch (err) {
        console.error("Error loading announcements:", err);
        setError("Failed to load announcements.");
      } finally {
        setLoading(false);
      }
    };

    fetchAnnouncements();
  }, []);

  // Fetch Categories
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const res = await api.get('/api/books/categories');
        setCategories(res.data);
      } catch (err) {
        console.error("Error loading categories:", err);
      }
    };
    fetchCategories();
  }, []);

  const handleDomainChange = (domain) => {
    if (selectedDomains.includes(domain)) {
      setSelectedDomains(selectedDomains.filter((d) => d !== domain));
    } else {
      setSelectedDomains([...selectedDomains, domain]);
    }
  };

  const renderStars = (rating = 4.5) => {
    return (
      <div className="stars">
        {[1, 2, 3, 4, 5].map((star) => (
          <span key={star} className={star <= Math.floor(rating) ? "star filled" : "star"}>
            ★
          </span>
        ))}
      </div>
    );
  };

  // Admin Delete
  const handleDelete = async (e, announcementId) => {
    e.preventDefault(); // Prevent link navigation
    if (!window.confirm("ADMIN ACTION: Are you sure you want to delete this listing?")) {
      return;
    }

    try {
      await api.delete(`/api/books/announcements/${announcementId}`);
      setBooks(books.filter((ann) => ann.id !== announcementId));
      alert("Announcement deleted by Admin.");
    } catch (error) {
      console.error("Delete error:", error);
      alert("Failed to delete announcement.");
    }
  };

  // Filtering Logic
  let filteredBooks = [...books];

  if (selectedDomains.length > 0) {
    filteredBooks = filteredBooks.filter((ann) =>
      ann.category && selectedDomains.includes(ann.category)
    );
  }

  if (selectedPrice) {
    filteredBooks = filteredBooks.filter((ann) => {
      const price = parseFloat(ann.price);
      switch (selectedPrice) {
        case "0-500": return price < 500;
        case "500-1000": return price >= 500 && price <= 1000;
        case "1000-2000": return price >= 1000 && price <= 2000;
        case "2000+": return price > 2000;
        default: return true;
      }
    });
  }

  if (selectedStatus) {
    filteredBooks = filteredBooks.filter(
      (ann) => ann.status?.toLowerCase() === selectedStatus.toLowerCase()
    );
  }

  if (searchQuery.trim()) {
    const query = searchQuery.toLowerCase();
    filteredBooks = filteredBooks.filter(
      (ann) =>
        ann.book?.title?.toLowerCase().includes(query) ||
        ann.book?.authors?.toLowerCase().includes(query) ||
        ann.user?.username?.toLowerCase().includes(query)
    );
  }

  // Sorting
  switch (sortBy) {
    case "price-low":
      filteredBooks.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
      break;
    case "price-high":
      filteredBooks.sort((a, b) => parseFloat(b.price) - parseFloat(a.price));
      break;
    default:
      break;
  }

  // Pagination
  const booksPerPage = 9;
  const totalPages = Math.ceil(filteredBooks.length / booksPerPage);
  const startIndex = (currentPage - 1) * booksPerPage;
  const currentBooks = filteredBooks.slice(startIndex, startIndex + booksPerPage);

  useEffect(() => {
    setCurrentPage(1);
  }, [selectedDomains, selectedPrice, searchQuery, sortBy, selectedStatus]);

  return (
    <div className="listing-page">
      <NavAdmin />

      <div className="listing-container">

        {/* SIDEBAR FILTERS - Exact match to Listing.jsx */}
        <aside className="filters-sidebar">
          <div className="filter-section">
            <h3 className="filter-title">Filter by Domain</h3>
            <div className="filter-options">
              {categories.length > 0 ? categories.map((domain) => (
                <label key={domain} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={selectedDomains.includes(domain)}
                    onChange={() => handleDomainChange(domain)}
                  />
                  <span>{domain}</span>
                </label>
              )) : <p className="text-sm text-gray-500">Loading...</p>}
            </div>
          </div>

          <div className="filter-section">
            <h3 className="filter-title">Filter by Status</h3>
            <div className="filter-options">
              {["Active", "Sold", "Reserved"].map((status) => (
                <label key={status} className="radio-label">
                  <input
                    type="radio"
                    name="status"
                    value={status}
                    checked={selectedStatus === status}
                    onChange={() => setSelectedStatus(selectedStatus === status ? "" : status)}
                  />
                  <span>{status}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="filter-section">
            <h3 className="filter-title">Filter by Price</h3>
            <div className="filter-options">
              {["0-500", "500-1000", "1000-2000", "2000+"].map((range) => (
                <label key={range} className="radio-label">
                  <input
                    type="radio"
                    name="price"
                    value={range}
                    checked={selectedPrice === range}
                    onChange={(e) => setSelectedPrice(e.target.value)}
                  />
                  <span>{range === "2000+" ? "> 2000 DA" : `${range} DA`}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={() => {
              setSelectedDomains([]);
              setSelectedPrice("");
              setSearchQuery("");
              setSortBy("default");
              setSelectedStatus("");
            }}
            className="clear-filters-btn"
          >
            Clear All Filters
          </button>
        </aside>

        {/* MAIN CONTENT */}
        <main className="books-content">
          {/* TOP BAR */}
          <div className="top-bar">
            <div className="search-section">
              <input
                type="text"
                className="search-input"
                placeholder="Search by title, author or seller..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button className="find-book-btn">Search</button>
            </div>

            <div className="sort-section">
              <select
                className="sort-dropdown"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="default">Default sorting</option>
                <option value="price-low">Price: Low to High</option>
                <option value="price-high">Price: High to Low</option>
              </select>
            </div>
          </div>

          {/* CONTENT GRID */}
          {loading ? (
            <div className="loading-container" style={{ textAlign: 'center', padding: '40px' }}>Loading announcements...</div>
          ) : filteredBooks.length === 0 ? (
            <div className="no-results">
              <p>No announcements found.</p>
              <button
                className="reset-btn"
                onClick={() => {
                  setSelectedDomains([]);
                  setSelectedPrice("");
                  setSearchQuery("");
                  setSortBy("default");
                  setSelectedStatus("");
                }}
              >
                Reset Filters
              </button>
            </div>
          ) : (
            <div className="books-grid">
              {currentBooks.map((ann) => (
                <Link
                  key={ann.id}
                  to={`/book/${ann.id}`}
                  className="book-card-link"
                >
                  <div className="book-card">
                    <div className="book-image-wrapper">
                      <img
                        src={ann.book?.cover_image_url || "https://via.placeholder.com/300x450"}
                        alt={ann.book?.title}
                        className="book-image"
                        onError={(e) => { e.target.src = "https://via.placeholder.com/300x450?text=No+Image"; }}
                      />
                      {/* Status Badge Over Image */}
                      <div style={{ position: 'absolute', top: '10px', right: '10px', background: 'rgba(0,0,0,0.7)', color: 'white', padding: '4px 8px', borderRadius: '4px', fontSize: '10px', fontWeight: 'bold', textTransform: 'uppercase' }}>
                        {ann.status}
                      </div>
                    </div>

                    <div className="book-info">
                      <h4 className="book-title">{ann.book?.title || "Untitled"}</h4>
                      {renderStars(4.5)} {/* Static rating for now */}

                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 'auto' }}>
                        <p className="book-price">{ann.price} DA</p>
                        <span style={{ fontSize: '10px', color: '#888', background: '#f0f0f0', padding: '2px 6px', borderRadius: '4px' }}>
                          {ann.user?.username}
                        </span>
                      </div>

                      {/* ADMIN ACTIONS */}
                      <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                        <button
                          className="buy-now-btn" // Reusing buy-now class for style consistency
                          style={{ background: '#ef4444', marginTop: 0 }} // Red for delete
                          onClick={(e) => handleDelete(e, ann.id)}
                        >
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
                            <FaTrash /> Delete
                          </div>
                        </button>
                      </div>

                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}

          {/* Pagination - Copied styles from Listing.css via existing classes */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="pagination-arrow"
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
              >
                ‹
              </button>
              <div className="pagination-dots">
                {[...Array(totalPages)].map((_, index) => {
                  const page = index + 1;
                  return (
                    <button
                      key={page}
                      className={`pagination-dot ${currentPage === page ? "active" : ""}`}
                      onClick={() => setCurrentPage(page)}
                    >
                      {page}
                    </button>
                  );
                })}
              </div>
              <button
                className="pagination-arrow"
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
              >
                ›
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default AnnouncementsAdmin;