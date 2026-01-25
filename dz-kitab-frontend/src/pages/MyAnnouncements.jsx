import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
// import "./MyAnnouncements.css";
import Navbar from "../components/navbar";
import Footer from "../components/footer";
import api from "../utils/api";
import { getCookie } from "../utils/cookies";
import { FaCheckCircle, FaExchangeAlt, FaTimesCircle } from "react-icons/fa";

const MyAnnouncements = () => {
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

  const API_BASE_URL = "http://localhost:8000";

  // ✅ Charger les annonces de l'utilisateur connecté (AVEC AUTH)
  useEffect(() => {
    const fetchMyAnnouncements = async () => {
      try {
        setLoading(true);
        setError(null);

        const token = getCookie("access_token");

        // ✅ Vérifier si l'utilisateur est connecté
        if (!token) {
          setError("Vous devez être connecté pour voir vos annonces");
          setLoading(false);
          navigate("/login");
          return;
        }

        console.log("Fetching announcements...");
        const response = await api.get('/api/books/my-announcements');

        console.log("Response:", response.data);

        // ✅ Gérer la structure de réponse du backend
        if (response.data?.announcements) {
          setBooks(response.data.announcements);
        } else if (Array.isArray(response.data)) {
          setBooks(response.data);
        } else {
          setBooks([]);
        }

        setLoading(false);
      } catch (err) {
        console.error("Error loading announcements:", err);
        setError(
          err.response?.data?.detail ||
          err.message ||
          "Erreur lors du chargement des annonces"
        );
        setLoading(false);
      }
    };

    fetchMyAnnouncements();
  }, [navigate]);

  // ✅ Charger les catégories depuis l'API
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

  const getStatusClasses = (status) => {
    switch (status?.toLowerCase()) {
      case "sold":
      case "vendu":
        return "text-gray-500";
      case "traded":
        return "text-[#F3A109]";
      case "active":
        return "text-[#090df3]";
      default:
        return "text-gray-400";
    }
  };

  // ✅ Delete avec authentification
  const handleDelete = async (announcementId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer cette annonce ?")) {
      return;
    }

    try {
      await api.delete(`/api/books/announcements/${announcementId}`);

      setBooks(books.filter((ann) => ann.id !== announcementId));
      alert("Annonce supprimée avec succès");
    } catch (error) {
      console.error("Delete error:", error);
      alert(error.response?.data?.detail || "Erreur lors de la suppression");
    }
  };

  // Filtering
  let filteredBooks = [...books];

  if (selectedDomains.length > 0) {
    filteredBooks = filteredBooks.filter((ann) =>
      ann.book?.categories?.split(",").some((c) =>
        selectedDomains.includes(c.trim())
      )
    );
  }

  if (selectedPrice) {
    filteredBooks = filteredBooks.filter((ann) => {
      const price = parseFloat(ann.price);
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

  if (selectedStatus) {
    filteredBooks = filteredBooks.filter(
      (ann) => ann.status?.toLowerCase() === selectedStatus.toLowerCase()
    );
  }

  if (searchQuery.trim()) {
    filteredBooks = filteredBooks.filter(
      (ann) =>
        ann.book?.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ann.book?.authors?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ann.book?.categories?.toLowerCase().includes(searchQuery.toLowerCase())
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
  const endIndex = startIndex + booksPerPage;
  const currentBooks = filteredBooks.slice(startIndex, endIndex);

  useEffect(() => {
    setCurrentPage(1);
  }, [selectedDomains, selectedPrice, searchQuery, sortBy, selectedStatus]);

  return (
    <>

      <div className="listing-page">
        <div className="listing-container">
          {/* Sidebar Filters */}
          <aside className="filters-sidebar">
            <div className="filter-section">
              <h3 className="filter-title">Filter by Domain</h3>
              <div className="filter-options">
                {categories.map((domain) => (
                  <label key={domain} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={selectedDomains.includes(domain)}
                      onChange={() => handleDomainChange(domain)}
                    />
                    <span>{domain}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="filter-section">
              <h3 className="filter-title">Filter by Status</h3>
              <div className="filter-options">
                {["Active", "Sold"].map((status) => (
                  <label key={status} className="radio-label">
                    <input
                      type="radio"
                      name="status"
                      value={status}
                      checked={selectedStatus === status}
                      onChange={() =>
                        setSelectedStatus(selectedStatus === status ? "" : status)
                      }
                    />
                    <span>{status}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="filter-section">
              <h3 className="filter-title">Filter by Price</h3>
              <div className="filter-options">
                {["0-500", "500-1000", "1000-2000", "2000+"].map((priceRange) => (
                  <label key={priceRange} className="radio-label">
                    <input
                      type="radio"
                      name="price"
                      value={priceRange}
                      checked={selectedPrice === priceRange}
                      onChange={(e) => setSelectedPrice(e.target.value)}
                    />
                    <span>
                      {priceRange === "0-500"
                        ? "< 500 DA"
                        : priceRange === "2000+"
                          ? "> 2000 DA"
                          : priceRange.replace("-", "–") + " DA"}
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
                setSearchQuery("");
                setSortBy("default");
                setSelectedStatus("");
              }}
            >
              Clear All Filters
            </button>
          </aside>

          {/* Books Content */}
          <main className="books-content">
            <div className="top-bar">
              <div className="search-section">
                <input
                  type="text"
                  className="search-input"
                  placeholder="Search..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                <button className="search-button">Find Book</button>
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

                <Link to="../AddNewAnnounce" className="publish-btn">+ Publish</Link>
              </div>
            </div>

            {loading ? (
              <div className="loading-state">
                <p>Loading your announcements...</p>
              </div>
            ) : error ? (
              <div className="error-state">
                <p style={{ color: "red" }}>{error}</p>
                <button onClick={() => window.location.reload()} className="reset-btn">
                  Retry
                </button>
              </div>
            ) : currentBooks.length === 0 ? (
              <div className="no-results">
                <p>
                  {books.length === 0
                    ? "You have not published any announcements yet."
                    : "No books match your filters."}
                </p>
                {books.length === 0 ? (
                  <Link to="../AddNewAnnounce" className="reset-btn">
                    Create Announcement
                  </Link>
                ) : (
                  <button text="Clear Filters"
                    className="w-40 h-12 rounded-[6px] bg-[#F3A109] text-white font-semibold leading-none transition-all duration-300 hover:bg-[#d89008] hover:-translate-y-0.5 hover:shadow-[0_4px_12px_rgba(243,161,9,0.3)] cursor-pointer"


                    onClick={() => {
                      setSelectedDomains([]);
                      setSelectedPrice("");
                      setSearchQuery("");
                      setSortBy("default");
                      setSelectedStatus("");
                    }}
                  >
                    Clear Filters
                  </button>
                )}
              </div>
            ) : (
              <div className="books-grid">
                {currentBooks.map((ann) => (
                  <div key={ann.id} className="book-card">
                    <Link to={`/book/${ann.id}`} className="book-card-link">
                      <div className="book-image-wrapper">
                        <img
                          src={
                            ann.book?.cover_image_url ||
                            (ann.custom_images ? `${API_BASE_URL}${ann.custom_images}` : null) ||
                            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='450'%3E%3Crect width='300' height='450' fill='%23cccccc'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='20' fill='%23666666'%3ENo Image%3C/text%3E%3C/svg%3E"}
                          alt={ann.book?.title || "Book cover"}
                          className="book-image"
                          onError={(e) => {
                            e.target.src = "https://via.placeholder.com/300x450/cccccc/666666?text=No+Image";
                          }}
                        />
                      </div>
                      <div className="book-info">
                        <h4 className="book-title">{ann.book?.title || "Title not available"}</h4>
                        <div className="flex items-center gap-20 my-4">
                          <p className="book-price whitespace-nowrap">
                            {ann.price} DA
                          </p>
                          <span
                            className={`px-2 py-1 rounded-full text-sm font-semibold flex items-center gap-1 ${getStatusClasses(
                              ann.status
                            )}`}
                          >
                            {ann.status?.toLowerCase() === "active" ? (
                              <>
                                <FaCheckCircle /> Active
                              </>
                            )

                              : ann.status?.toLowerCase() === "sold" || ann.status?.toLowerCase() === "vendu" ? (
                                <>
                                  <FaTimesCircle /> Sold
                                </>
                              ) : (
                                ann.status
                              )}
                          </span>
                        </div>
                      </div>
                    </Link>
                    <div className="flex gap-8 mt-4">
                      <Link
                        to={`/edit/${ann.id}`}
                        className="flex-1 text-center border border-[#090df3] text-[#090df3]
                                   rounded-xl py-2 text-sm font-medium hover:bg-[#090df3] hover:text-white transition"
                      >
                        Modify
                      </Link>

                      <button
                        onClick={() => handleDelete(ann.id)}
                        className="flex-1 border border-red-500 text-red-500
                                   rounded-xl py-2 text-sm font-medium hover:bg-red-500 hover:border-red-500 hover:text-white transition"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="pagination">
              <button
                onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="pagination-btn"
              >
                &lt;
              </button>

              {Array.from({ length: totalPages }, (_, i) => (
                <button
                  key={i + 1}
                  onClick={() => setCurrentPage(i + 1)}
                  className={`pagination-btn ${currentPage === i + 1 ? "active" : ""}`}
                >
                  {i + 1}
                </button>
              ))}

              <button
                onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="pagination-btn"
              >
                &gt;
              </button>
            </div>
          </main>
        </div>
      </div>

      <Footer />
    </>
  );
};

export default MyAnnouncements;