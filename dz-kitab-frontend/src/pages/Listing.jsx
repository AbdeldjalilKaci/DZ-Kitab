import React, { useState } from "react";
import { Link } from "react-router-dom";
import { CiHeart } from "react-icons/ci";
import { FaHeart } from "react-icons/fa";
import Header from "../components/header";
import Footer from "../components/footer";
import { booksData } from "../data/booksData";
import { useWishlist } from "../context/WishlistContext";
import "./Listing.css";

const Listing = () => {
  const [selectedDomains, setSelectedDomains] = useState([]);
  const [selectedPrice, setSelectedPrice] = useState("");
  const [selectedRating, setSelectedRating] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("default");
  const [currentPage, setCurrentPage] = useState(1);
  const { isInWishlist, toggleWishlist } = useWishlist();

  const handleDomainChange = (domain) => {
    if (selectedDomains.includes(domain)) {
      setSelectedDomains(selectedDomains.filter((d) => d !== domain));
    } else {
      setSelectedDomains([...selectedDomains, domain]);
    }
  };

  const renderStars = (rating) => {
    return (
      <div className="stars">
        {[1, 2, 3, 4, 5].map((star) => (
          <span key={star} className={star <= rating ? "star filled" : "star"}>
            ★
          </span>
        ))}
      </div>
    );
  };

  // Filter and sort books
  let filteredBooks = [...booksData];

  // Filter by domain
  if (selectedDomains.length > 0) {
    filteredBooks = filteredBooks.filter((book) =>
      selectedDomains.includes(book.domain)
    );
  }

  // Filter by price
  if (selectedPrice) {
    filteredBooks = filteredBooks.filter((book) => {
      const price = parseFloat(book.price);
      switch (selectedPrice) {
        case "0-500":
          return price < 500;
        case "500-1000":
          return price >= 500 && price <= 1000;
        case "1000-2000":
          return price >= 1000 && price <= 2000;
        case "2000+":
          return price > 2000;
        default:
          return true;
      }
    });
  }

  // Filter by rating
  if (selectedRating > 0) {
    filteredBooks = filteredBooks.filter(
      (book) => book.rating === selectedRating
    );
  }

  // Filter by search query
  if (searchQuery.trim()) {
    filteredBooks = filteredBooks.filter(
      (book) =>
        book.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        book.author.toLowerCase().includes(searchQuery.toLowerCase()) ||
        book.domain.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }

  // Sort books
  switch (sortBy) {
    case "price-low":
      filteredBooks.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
      break;
    case "price-high":
      filteredBooks.sort((a, b) => parseFloat(b.price) - parseFloat(a.price));
      break;
    case "rating":
      filteredBooks.sort((a, b) => b.rating - a.rating);
      break;
    default:
      break;
  }

  // Pagination logic
  const booksPerPage = 9;
  const totalPages = Math.ceil(filteredBooks.length / booksPerPage);
  const startIndex = (currentPage - 1) * booksPerPage;
  const endIndex = startIndex + booksPerPage;
  const currentBooks = filteredBooks.slice(startIndex, endIndex);

  // Reset to page 1 when filters change
  React.useEffect(() => {
    setCurrentPage(1);
  }, [selectedDomains, selectedPrice, selectedRating, searchQuery, sortBy]);

  return (
    <div className="listing-page">
      <div className="listing-container">
        {/* LEFT SIDEBAR - FILTERS */}
        <aside className="filters-sidebar">
          <div className="filter-section">
            <h3 className="filter-title">Filter by Domain</h3>
            <div className="filter-options">
              {["Mathematics", "Physics", "Science", "Philosophy"].map(
                (domain) => (
                  <label key={domain} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={selectedDomains.includes(domain)}
                      onChange={() => handleDomainChange(domain)}
                    />
                    <span>{domain}</span>
                  </label>
                )
              )}
            </div>
          </div>

          <div className="filter-section">
            <h3 className="filter-title">Filter by Price</h3>
            <div className="filter-options">
              <label className="radio-label">
                <input
                  type="radio"
                  name="price"
                  value="0-500"
                  checked={selectedPrice === "0-500"}
                  onChange={(e) => setSelectedPrice(e.target.value)}
                />
                <span>&lt; 500 DA</span>
              </label>
              <label className="radio-label">
                <input
                  type="radio"
                  name="price"
                  value="500-1000"
                  checked={selectedPrice === "500-1000"}
                  onChange={(e) => setSelectedPrice(e.target.value)}
                />
                <span>500–1000 DA</span>
              </label>
              <label className="radio-label">
                <input
                  type="radio"
                  name="price"
                  value="1000-2000"
                  checked={selectedPrice === "1000-2000"}
                  onChange={(e) => setSelectedPrice(e.target.value)}
                />
                <span>1000–2000 DA</span>
              </label>
              <label className="radio-label">
                <input
                  type="radio"
                  name="price"
                  value="2000+"
                  checked={selectedPrice === "2000+"}
                  onChange={(e) => setSelectedPrice(e.target.value)}
                />
                <span>&gt; 2000 DA</span>
              </label>
            </div>
          </div>

          <div className="filter-section">
            <h3 className="filter-title">Filter by Rating</h3>
            <div className="filter-options">
              {[5, 4, 3, 2, 1].map((rating) => (
                <label key={rating} className="rating-label">
                  <input
                    type="radio"
                    name="rating"
                    value={rating}
                    checked={selectedRating === rating}
                    onChange={() =>
                      setSelectedRating(selectedRating === rating ? 0 : rating)
                    }
                  />
                  <span className="rating-stars">
                    {[...Array(rating)].map((_, i) => (
                      <span key={i} className="star filled">
                        ★
                      </span>
                    ))}
                    {[...Array(5 - rating)].map((_, i) => (
                      <span key={i} className="star">
                        ★
                      </span>
                    ))}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <button
            className="clear-filters-btn"
            onClick={() => {
              setSelectedDomains([]);
              setSelectedPrice("");
              setSelectedRating(0);
              setSearchQuery("");
              setSortBy("default");
            }}
          >
            Clear All Filters
          </button>
        </aside>

        {/* RIGHT CONTENT AREA */}
        <main className="books-content">
          {/* TOP BAR */}
          <div className="top-bar">
            <div className="search-section">
              <input
                type="text"
                className="search-input"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button className="find-book-btn">Find Book</button>
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
                <option value="rating">Rating</option>
              </select>
            </div>
          </div>

          {/* BOOK GRID */}
          {currentBooks.length === 0 ? (
            <div className="no-results">
              <p>No books found matching your filters.</p>
              <button
                className="reset-btn"
                onClick={() => {
                  setSelectedDomains([]);
                  setSelectedPrice("");
                  setSelectedRating(0);
                  setSearchQuery("");
                  setSortBy("default");
                }}
              >
                Clear Filters
              </button>
            </div>
          ) : (
            <div className="books-grid">
              {currentBooks.map((book) => (
                <Link
                  key={book.id}
                  to={`/book/${book.id}`}
                  className="book-card-link"
                >
                  <div className="book-card">
                    <div className="book-image-wrapper">
                      <img
                        src={book.image}
                        alt={book.title}
                        className="book-image"
                      />
                    </div>
                    <div className="book-info">
                      <h4 className="book-title">{book.title}</h4>
                      {renderStars(book.rating)}
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                        }}
                      >
                        <p className="book-price">{book.price} DA</p>
                        <button
                          className="favorite-btn"
                          onClick={(e) => {
                            e.preventDefault();
                            toggleWishlist(book.id);
                          }}
                          style={{
                            background: "none",
                            border: "none",
                            cursor: "pointer",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            position: "static",
                            boxShadow: "none",
                            width: "auto",
                            height: "auto",
                            padding: "5px",
                          }}
                        >
                          {isInWishlist(book.id) ? (
                            <FaHeart size={26} color="red" />
                          ) : (
                            <CiHeart size={30} color="black" />
                          )}
                        </button>
                      </div>
                      <button
                        className="buy-now-btn"
                        onClick={(e) => e.preventDefault()}
                      >
                        Buy now
                      </button>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}

          {/* PAGINATION */}
          {currentBooks.length > 0 && totalPages > 1 && (
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
                      className={`pagination-dot ${
                        currentPage === page ? "active" : ""
                      }`}
                      onClick={() => setCurrentPage(page)}
                    >
                      {page}
                    </button>
                  );
                })}
              </div>
              <button
                className="pagination-arrow"
                onClick={() =>
                  setCurrentPage(Math.min(totalPages, currentPage + 1))
                }
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

export default Listing;