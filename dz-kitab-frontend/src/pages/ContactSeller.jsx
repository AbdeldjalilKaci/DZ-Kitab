import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../utils/api";
import "./ContactSeller.css";

const ContactSeller = () => {
  const location = useLocation();
  const navigate = useNavigate();
  // Get book from navigation state (passed from Listing or BookDetails)
  const book = location.state?.book;

  const [formData, setFormData] = useState({
    address: "",
    phone: "",
    message: "",
  });
  const [loading, setLoading] = useState(false);

  // Redirect if no book data
  useEffect(() => {
    if (!book) {
      // Optional: Could fetch by ID from URL if we changed route to /contact-seller/:id
      // For now, assume state passing.
    }
  }, [book, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async () => {
    if (!formData.address || !formData.phone) {
      alert("Address and phone number are required");
      return;
    }

    if (!book) return;

    try {
      setLoading(true);
      // Create conversation or send message
      // Endpoint: POST /api/messages/conversations?other_user_id=...&announcement_id=...
      // Then POST message?
      // Or simpler: The backend might not have a direct "Contact Seller" single endpoint yet based on previous files.
      // Let's assume we create a conversation or send a message.
      // Checking backend standard: usually start conversation with initial message.
      // Let's try to create a conversation first.

      // 1. Check/Create conversation
      // For simplicity, let's assume we just send a message to start it.
      // We need the seller's user ID.
      // 'book' object usually comes from Listing, which has 'user' (seller) object?
      // Let's verify structure. In Listing.jsx: book object has title, author... but maybe not user_id explicitly in the manual map?
      // Listing.jsx map: id, title, author... user_id is in response.data.announcements but mappedBooks might miss it.
      // We need to ensure we pass the seller ID.

      // If we don't have seller ID, we can't send.
      // Assuming book.user_id or book.seller_id exists.

      const sellerId = book.user?.id || book.user_id;

      if (!sellerId) {
        alert("Error: Seller information missing.");
        return;
      }

      // Construct initial message
      const fullMessage = `
**Interest in:** ${book.title}
**Contact Info:**
Phone: ${formData.phone}
Address: ${formData.address}

${formData.message}
        `.trim();

      // API call to create conversation/send message
      // Using the logic from Messages.jsx: 
      // POST /api/messages/conversations/{id}/messages ?
      // We first need a conversation. 
      // Let's try POST /api/messages/conversations with params

      await api.post('/api/messages/conversations', {
        participant_id: sellerId,
        announcement_id: book.id, // announcement ID
        initial_message: fullMessage
      });

      alert("Message sent successfully!");
      navigate('/message'); // Go to messages to see the chat

    } catch (error) {
      console.error("Error sending message:", error);
      alert("Failed to send message. " + (error.response?.data?.detail || ""));
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate(-1);
  };

  if (!book) {
    return (
      <div className="contact-seller-wrapper">
        <div className="container mx-auto p-4 text-center">
          <h2>No book selected.</h2>
          <button onClick={() => navigate('/catalog')} className="btn btn-primary">Go to Catalog</button>
        </div>
      </div>
    );
  }

  return (
    <div className="contact-seller-wrapper">
      <div className="contact-seller-card">
        <div className="title-section">
          <h2 className="main-title">Contact the Seller</h2>
          <div className="title-underline"></div>
        </div>

        <div className="form-container">
          <div className="book-cover-section">
            <div className="book-cover-wrapper">
              {book?.image ? (
                <img
                  src={book.image}
                  alt={book.title}
                  className="book-cover-img"
                />
              ) : (
                <div className="book-cover-placeholder">
                  <div className="placeholder-content">
                    <div className="placeholder-icon">✕</div>
                    <div className="placeholder-title">{book.title}</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="form-fields">
            <div className="input-group">
              <label className="input-label">Title</label>
              <input
                type="text"
                value={book?.title || "Book Title"}
                disabled
                className="input-field input-readonly"
              />
            </div>

            {/* Show Seller Email if available */}
            <div className="input-group">
              <label className="input-label">Seller Email</label>
              <input
                type="email"
                value={book.user?.email || "N/A"}
                disabled
                className="input-field input-readonly"
              />
            </div>

            <div className="input-group">
              <label className="input-label">
                My Address <span style={{ color: "red" }}>*</span>
              </label>
              <input
                type="text"
                name="address"
                value={formData.address}
                onChange={handleChange}
                className="input-field"
                placeholder="Your address"
                required
              />
            </div>

            <div className="input-group">
              <label className="input-label">
                My Phone <span style={{ color: "red" }}>*</span>
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="input-field"
                placeholder="05xxxxxxxx"
                required
              />
            </div>

            <div className="input-group">
              <label className="input-label">Message</label>
              <textarea
                name="message"
                value={formData.message}
                onChange={handleChange}
                className="textarea-field"
                placeholder="Describe your request"
              />
            </div>
          </div>

          <div className="button-group">
            <button className="btn btn-cancel" onClick={handleCancel}>
              Cancel
            </button>
            <button className="btn btn-send" onClick={handleSubmit} disabled={loading}>
              {loading ? "Sending..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactSeller;
