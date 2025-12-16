import React, { useState } from 'react';
import './addnewannouce.css'

function AddAnnounce() {
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        cover: null,
        isbn: '',
        title: '',
        description: '',
        pages: '',
        domain: '',
        author: '',
        price: '',
        publicationYear: '',
        status: '',
        eta: ''
    });

    const handleInputChange = (e) => {
        const { name, value, files } = e.target;
        if (name === 'cover' && files[0]) {
            setFormData({
                ...formData,
                cover: URL.createObjectURL(files[0])
            });
        } else {
            setFormData({
                ...formData,
                [name]: value
            });
        }
    };

    const nextStep = () => {
        setStep(step + 1);
    };

    const prevStep = () => {
        setStep(step - 1);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
    };

    return (
        <div className="app">
            <h1 className="main-title">
                {step === 1 ? 'Add New Announcement' : 'Add New Book'}
            </h1>

            <div className="stepper">
                <div className={`step ${step >= 1 ? 'active' : ''}`}>
                    <div className="step-circle">1</div>
                    <span>Cover & Info</span>
                </div>
                <div className="step-line"></div>
                <div className={`step ${step >= 2 ? 'active' : ''}`}>
                    <div className="step-circle">2</div>
                    <span>Book Details</span>
                </div>
                <div className="step-line"></div>
                <div className={`step ${step >= 3 ? 'active' : ''}`}>
                    <div className="step-circle">3</div>
                    <span>Additional Info</span>
                </div>
            </div>

            <form className="form-container" onSubmit={handleSubmit}>
                {step === 1 && (
                    <div className="form-step">
                        <h2>Add Cover</h2>

                        <div className="upload-section">
                            <div className="cover-upload">
                                <label htmlFor="cover-upload" className="upload-label">
                                    {formData.cover ? (
                                        <img src={formData.cover} alt="Book Cover" className="cover-preview" />
                                    ) : (
                                        <>
                                            <div className="upload-icon">📚</div>
                                            <span>Upload Book Cover</span>
                                            <span className="upload-hint">Click to upload cover image</span>
                                        </>
                                    )}
                                </label>
                                <input
                                    type="file"
                                    id="cover-upload"
                                    name="cover"
                                    accept="image/*"
                                    onChange={handleInputChange}
                                    className="file-input"
                                />
                            </div>
                        </div>

                        <div className="form-group-announce">
                            <label>Add ISBN</label>
                            <input
                                type="text"
                                name="isbn"
                                placeholder="Write book ISBN"
                                value={formData.isbn}
                                onChange={handleInputChange}
                                required
                            />
                        </div>

                        <div className="form-group-announce">
                            <label>Add Title</label>
                            <input
                                type="text"
                                name="title"
                                placeholder="Write the title..."
                                value={formData.title}
                                onChange={handleInputChange}
                                required
                            />
                        </div>

                        <div className="form-group-announce">
                            <label>Add Description</label>
                            <textarea
                                name="description"
                                placeholder="Write the description..."
                                value={formData.description}
                                onChange={handleInputChange}
                                rows="4"
                                required
                            />
                        </div>
                    </div>
                )}

                {step === 2 && (

                    <div className="form-step">
                        <div className="form-group-announce">
                            <label>Add Domain</label>
                            <input
                                type="text"
                                name="domain"
                                placeholder="Write the domain"
                                value={formData.domain}
                                onChange={handleInputChange}
                                required
                            />
                        </div>
                        <div className="form-group-announce">
                            <label>Add Publication Year</label>
                            <input
                                type="number"
                                name="publicationYear"
                                placeholder="Enter publication year"
                                value={formData.publicationYear}
                                onChange={handleInputChange}
                                required
                            />
                        </div>

                        <div className="form-group-announce">
                            <label>Add Author</label>
                            <input
                                type="text"
                                name="author"
                                placeholder="Write the author"
                                value={formData.author}
                                onChange={handleInputChange}
                                required
                            />
                        </div>
                        <div className="form-group-announce">
                            <label>Add Status</label>
                            <select
                                name="status"
                                value={formData.status}
                                onChange={handleInputChange}
                                required
                            >
                                <option value="">Select status</option>
                                <option value="available">Available</option>
                                <option value="out_of_stock">Out of Stock</option>
                                <option value="pre_order">Pre-order</option>
                            </select>
                        </div>
                    </div>
                )}

                {step === 3 && (
                    <div className="form-step">
                        <div className="form-group-announce">
                            <label>Add ETA</label>
                            <input
                                type="text"
                                name="eta"
                                placeholder="Write the ETA"
                                value={formData.eta}
                                onChange={handleInputChange}
                            />
                        </div>
                        <div className="form-group-announce">
                            <label>Add Pages Number</label>
                            <input
                                type="number"
                                name="pages"
                                placeholder="Enter pages number"
                                value={formData.pages}
                                onChange={handleInputChange}
                                required
                            />
                        </div>

                        <div className="form-group-announce">
                            <label>Add Price</label>
                            <input
                                type="text"
                                name="price"
                                placeholder="Write the price"
                                value={formData.price}
                                onChange={handleInputChange}
                                required
                            />
                        </div>
                    </div>
                )}

                <div className="navigation-buttons">
                    {step > 1 && (
                        <button type="button" onClick={prevStep} className="btn btn-secondary">
                            Previous
                        </button>
                    )}

                    {step < 3 ? (
                        <button type="button" onClick={nextStep} className="btn btn-primary">
                            Next
                        </button>
                    ) : (
                        <button type="submit" className="addbook  btn btn-primary">
                            Add New Book
                        </button>
                    )}
                </div>
            </form>
        </div>
    );
}

export default AddAnnounce;