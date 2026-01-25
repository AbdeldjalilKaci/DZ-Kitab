import React, { useState, useEffect } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { CiHeart } from "react-icons/ci";
import { FaHeart } from "react-icons/fa";
import Header from "../components/header";
import Footer from "../components/footer";
import { useWishlist } from "../context/WishlistContext";
import "./BookDetails.css";
import api from "../utils/api";
import { getCookie } from "../utils/cookies";


const BookDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [userRating, setUserRating] = useState(0);
  const [ratingComment, setRatingComment] = useState('');
  const [book, setBook] = useState(null);
  const [seller, setSeller] = useState(null);
  const [sellerRatings, setSellerRatings] = useState([]);
  const [recommendedBooks, setRecommendedBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submittingRating, setSubmittingRating] = useState(false);
  const { isInWishlist, toggleWishlist } = useWishlist();

  // Scroll to top when book ID changes
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [id]);

  useEffect(() => {
    const fetchBookDetails = async () => {
      setLoading(true);
      try {
        const response = await api.get(`/api/books/announcements/${id}`);
        const ann = response.data;
        const mappedBook = {
          id: ann.id,
          title: ann.book.title,
          author: ann.book.authors,
          price: ann.price,
          rating: 4.5,
          image: ann.book.cover_image_url || 'https://via.placeholder.com/150',
          domain: ann.category || 'General',
          description: ann.description,
          isbn: ann.book.isbn,
          status: ann.status,
          pages: ann.page_count,
          year: ann.publication_date,
          user: ann.user // Pass seller info to ContactSeller
        };
        setBook(mappedBook);
        setSeller(ann.user);

        // Fetch seller ratings
        try {
          const ratingsResponse = await api.get(`/api/ratings/seller/${ann.user.id}`);
          setSellerRatings(ratingsResponse.data.ratings || []);
        } catch (error) {
          console.error("Error fetching ratings:", error);
        }

        // Fetch recommendations (could be simply from all announcements for now)
        const recResponse = await api.get('/api/books/announcements?limit=5');
        const recMapped = recResponse.data.announcements
          .filter(a => a.id !== parseInt(id))
          .slice(0, 3)
          .map(a => ({
            id: a.id,
            title: a.book.title,
            image: a.book.cover_image_url || 'https://via.placeholder.com/150',
            price: a.price,
            rating: 4.0
          }));
        setRecommendedBooks(recMapped);

      } catch (error) {
        console.error("Error fetching book details:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchBookDetails();
  }, [id]);

  // If loading
  if (loading) {
    return (
      <div className="book-details-page">
        <Header />
        <div className="book-details-container">
          <p>Loading book details...</p>
        </div>
        <Footer />
      </div>
    );
  }

  // If book not found
  if (!book) {
    return (
      <div className="book-details-page">
        <Header />
        <div className="book-details-container">
          <p>Book not found</p>
          <Link to="/catalog" className="back-link">
            ← Back to Catalogue
          </Link>
        </div>
        <Footer />
      </div>
    );
  }
  const handleSubmitRating = async () => {
    // Check if user is logged in
    const access_token = getCookie('access_token');
    if (!access_token) {
      alert("Please login to submit a rating.");
      navigate('/login');
      return;
    }

    if (userRating === 0) {
      alert("Please select a rating before submitting.");
      return;
    }

    setSubmittingRating(true);
    try {
      await api.post('/api/ratings/', {
        announcement_id: parseInt(id),
        rating: userRating,
        comment: ratingComment || null
      });
      alert("Rating submitted successfully!");
      setUserRating(0);
      setRatingComment('');

      // Refresh ratings
      const ratingsResponse = await api.get(`/api/ratings/seller/${seller.id}`);
      setSellerRatings(ratingsResponse.data.ratings || []);
    } catch (error) {
      console.error("Error submitting rating:", error);
      const errorMsg = error.response?.data?.detail || "Failed to submit rating";
      alert(errorMsg);
    } finally {
      setSubmittingRating(false);
    }
  };

  const renderStars = (rating, interactive = false, size = "medium") => {
    return (
      <div className={`stars stars-${size}`}>
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={star <= rating ? "star filled" : "star"}
            onClick={interactive ? () => setUserRating(star) : undefined}
            style={interactive ? { cursor: "pointer" } : {}}
          >
            ★
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="book-details-page">
      <div className="book-details-container">
        {/* BACK LINK */}
        <Link to="/catalog" className="back-link">
          ← To Catalogue
        </Link>

        {/* MAIN BOOK DETAILS SECTION */}
        <div className="book-details-main">
          {/* LEFT COLUMN - IMAGE */}
          <div className="book-image-section">
            <img
              src={book.image}
              alt={book.title}
              className="book-detail-image"
            />
          </div>

          {/* RIGHT COLUMN - DETAILS */}
          <div className="book-info-section">
            <div className="book-header">
              <div className="title-rating-row">
                <h1 className="book-detail-title">{book.title}</h1>
                {renderStars(book.rating)}
              </div>
              <p className="book-author">by {book.author}</p>
            </div>

            <div className="book-metadata">
              <div className="metadata-item">
                <span className="metadata-label">Pages:</span>
                <span className="metadata-value">{book.pages}</span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">Domain:</span>
                <span className="metadata-value">{book.domain}</span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">Publication Year:</span>
                <span className="metadata-value">{book.year}</span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">ISBN:</span>
                <span className="metadata-value">{book.isbn}</span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">Status:</span>
                <span
                  className={`metadata-value status-${book.status.toLowerCase()}`}
                >
                  {book.status}
                </span>
              </div>
            </div>

            <div className="book-actions">
              <div className="price-rating-row">
                <div className="price-section">
                  <span className="book-detail-price">{book.price} DA</span>
                </div>
                <div className="add-rating">
                  <span className="add-rating-label">Add Rating:</span>
                  {renderStars(userRating, true, "small")}
                </div>
              </div>
              <div className="action-buttons">
                <button className="buy-now-btn-detail" onClick={() => navigate('/contact-seller', { state: { book: book } })}>Buy Now</button>
                <button
                  className="favorite-btn-detail"
                  onClick={() => toggleWishlist(book.id)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  {isInWishlist(book.id) ? (
                    <FaHeart size={20} color="red" />
                  ) : (
                    <CiHeart size={24} color="black" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* DESCRIPTION SECTION */}
        <div className="book-description-section">
          <h2 className="section-title">Description</h2>
          <p className="description-text">{book.description}</p>
        </div>

        {/* RATINGS SECTION */}
        <div className="ratings-section">
          <h2 className="section-title">Seller Ratings</h2>

          {/* Submit Rating Form */}
          <div className="submit-rating-form">
            <h3>Rate this seller</h3>
            <div className="rating-input">
              <span>Your Rating:</span>
              {renderStars(userRating, true, "medium")}
            </div>
            <textarea
              placeholder="Add a comment (optional)..."
              value={ratingComment}
              onChange={(e) => setRatingComment(e.target.value)}
              rows="3"
              style={{ width: '100%', padding: '10px', marginTop: '10px', borderRadius: '5px', border: '1px solid #ddd' }}
            />
            <button
              onClick={handleSubmitRating}
              disabled={submittingRating}
              style={{ marginTop: '10px', padding: '10px 20px', backgroundColor: '#1314d7', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
            >
              {submittingRating ? 'Submitting...' : 'Submit Rating'}
            </button>
          </div>

          {/* Display Ratings */}
          <div className="ratings-list" style={{ marginTop: '30px' }}>
            {sellerRatings.length > 0 ? (
              sellerRatings.map((rating) => (
                <div key={rating.id} className="rating-card" style={{ padding: '15px', marginBottom: '15px', border: '1px solid #eee', borderRadius: '5px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong>{rating.buyer_username}</strong>
                    {renderStars(rating.rating, false, "small")}
                  </div>
                  {rating.comment && (
                    <p style={{ marginTop: '10px', color: '#666' }}>{rating.comment}</p>
                  )}
                  <small style={{ color: '#999' }}>{new Date(rating.created_at).toLocaleDateString()}</small>
                </div>
              ))
            ) : (
              <p style={{ color: '#999' }}>No ratings yet. Be the first to rate this seller!</p>
            )}
          </div>
        </div>

        {/* ALSO RECOMMENDED SECTION */}
        <div className="recommended-section">
          <h2 className="section-title">Also Recommended</h2>
          <div className="recommended-grid">
            {recommendedBooks.map((recBook) => (
              <Link
                key={recBook.id}
                to={`/book/${recBook.id}`}
                className="recommended-card-link"
              >
                <div className="recommended-card">
                  <div className="recommended-image-wrapper">
                    <img
                      src={recBook.image}
                      alt={recBook.title}
                      className="recommended-image"
                    />
                  </div>
                  <div className="recommended-info">
                    <h4 className="recommended-title">{recBook.title}</h4>
                    {renderStars(recBook.rating, false, "small")}
                    <p className="recommended-price">{recBook.price} DA</p>
                    <button
                      className="recommended-buy-btn"
                    >
                      Buy now
                    </button>

                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookDetails;
