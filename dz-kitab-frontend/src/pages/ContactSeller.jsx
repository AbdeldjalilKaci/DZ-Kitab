import React, { useState, useEffect } from "react";
import "./ContactSeller.css";

const ContactSellerForm = ({ book, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    email: "",
    address: "",
    phone: "",
    message: "",
  });

  useEffect(() => {
    setFormData((prev) => ({
      ...prev,
      email: "jammy@gmail.com",
    }));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = () => {
    if (!formData.address || !formData.phone) {
      alert("Address and phone number are required");
      return;
    }

    onSubmit({
      ...formData,
      title: book?.title,
    });
  };

  const handleCancel = () => {
    setFormData({
      email: "jammy@gmail.com",
      address: "",
      phone: "",
      message: "",
    });
    if (onClose) onClose();
  };

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
                    <div className="placeholder-title">THE MATH</div>
                    <div className="placeholder-subtitle">BOOK</div>
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

            <div className="input-group">
              <label className="input-label">Email</label>
              <input
                type="email"
                value={formData.email}
                disabled
                className="input-field input-readonly"
              />
            </div>

            <div className="input-group">
              <label className="input-label">
                Address <span style={{ color: "red" }}>*</span>
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
                Phone <span style={{ color: "red" }}>*</span>
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
            <button className="btn btn-send" onClick={handleSubmit}>
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactSellerForm;
