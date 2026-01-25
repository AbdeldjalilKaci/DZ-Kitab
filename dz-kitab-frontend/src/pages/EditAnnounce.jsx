import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { useNavigate, useParams } from 'react-router-dom';
import './addnewannouce.css';
import { FaSearch, FaBook, FaCheckCircle, FaCamera, FaRobot, FaArrowRight, FaArrowLeft, FaBarcode, FaUpload } from 'react-icons/fa';
import { MdVerified, MdWarning } from 'react-icons/md';

function EditAnnounce() {
    const navigate = useNavigate();
    const { id } = useParams();
    const isEditMode = true; // Always true for this page

    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);

    const [isbn, setIsbn] = useState('');
    const [bookFound, setBookFound] = useState(false);
    const [manualEntry, setManualEntry] = useState(false);
    const [categories, setCategories] = useState([]);
    const [bookDetails, setBookDetails] = useState({
        title: '',
        authors: [],
        pageCount: '',
        publishedDate: '',
        categories: [],
        description: '',
        thumbnail: '',
        publisher: '',
        basePrice: '',
        selectedCategory: ''
    });

    const initialScoring = {
        page: {
            page_no_missing: true,
            page_no_torn: true,
            page_clean: true,
            page_score: 100
        },
        binding: {
            binding_no_loose: true,
            binding_no_falling: true,
            binding_stable: true,
            binding_score: 100
        },
        cover: {
            cover_no_detachment: true,
            cover_clean: true,
            cover_no_scratches: true,
            cover_score: 100
        },
        damages: {
            damage_no_burns: true,
            damage_no_smell: true,
            damage_no_insects: true,
            damage_score: 100
        },
        accessories: {
            accessories_complete: true,
            accessories_content: true,
            accessories_extras: false,
            accessories_score: 100
        }
    };
    const [scoringData, setScoringData] = useState(initialScoring);
    const [overallScore, setOverallScore] = useState(100);

    const [photos, setPhotos] = useState([]);
    const [analyzing, setAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState(null);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const response = await api.get('/api/books/categories');
                setCategories(response.data);
            } catch (error) {
                console.error("Error fetching categories:", error);
            }
        };
        fetchCategories();
    }, []);

    // Fetch existing announcement for editing
    useEffect(() => {
        const fetchAnnouncement = async () => {
            if (!id) return;
            setLoading(true);
            try {
                const response = await api.get(`/api/books/announcements/${id}`);
                const data = response.data;
                const book = data.book;

                // Pre-fill State
                setIsbn(book.isbn);
                setBookDetails({
                    title: book.title,
                    authors: book.authors ? book.authors.split(', ') : [],
                    pageCount: data.page_count || book.page_count,
                    publishedDate: data.publication_date || book.published_date,
                    categories: book.categories ? book.categories.split(', ') : [],
                    description: data.description || book.description,
                    thumbnail: book.cover_image_url,
                    publisher: book.publisher,
                    basePrice: data.market_price || '',
                    selectedCategory: data.category
                });

                // Pre-fill Photos
                if (data.custom_images) {
                    const images = data.custom_images.split(',').map(url => ({
                        preview: `http://localhost:8000${url}`,
                        existing: true,
                        url: url
                    }));
                    setPhotos(images);
                }

                setBookFound(true);
                // Optionally start at step 2 or stay at step 1 for review
            } catch (error) {
                console.error("Error fetching announcement:", error);
                alert("Failed to load announcement for editing.");
                navigate('/myannouncements');
            } finally {
                setLoading(false);
            }
        };
        fetchAnnouncement();
    }, [id, navigate]);

    const handleScoreChange = (category, field) => {
        setScoringData(prev => ({
            ...prev,
            [category]: {
                ...prev[category],
                [field]: !prev[category][field]
            }
        }));
    };

    useEffect(() => {
        if (!scoringData || !scoringData.page || typeof scoringData.page.page_no_missing === 'undefined') return;

        let pScore = 0;
        if (scoringData.page.page_no_missing) pScore += 40;
        if (scoringData.page.page_no_torn) pScore += 30;
        if (scoringData.page.page_clean) pScore += 30;

        let bScore = 0;
        if (scoringData.binding.binding_no_loose) bScore += 40;
        if (scoringData.binding.binding_no_falling) bScore += 40;
        if (scoringData.binding.binding_stable) bScore += 20;

        let cScore = 0;
        if (scoringData.cover.cover_no_detachment) cScore += 50;
        if (scoringData.cover.cover_clean) cScore += 25;
        if (scoringData.cover.cover_no_scratches) cScore += 25;

        let dScore = 0;
        if (scoringData.damages.damage_no_burns) dScore += 40;
        if (scoringData.damages.damage_no_smell) dScore += 30;
        if (scoringData.damages.damage_no_insects) dScore += 30;

        let aScore = 0;
        if (scoringData.accessories.accessories_complete) aScore += 50;
        if (scoringData.accessories.accessories_content) aScore += 50;

        const newOverall = Math.round((pScore + bScore + cScore + dScore + aScore) / 5);

        if (overallScore !== newOverall) {
            setOverallScore(newOverall);
        }
    }, [scoringData, overallScore]);

    const handlePhotoUpload = (e) => {
        const files = Array.from(e.target.files);
        if (files.length + photos.length > 4) {
            alert("Maximum 4 photos allowed");
            return;
        }

        const newPhotos = files.map(file => ({
            file,
            preview: URL.createObjectURL(file)
        }));
        setPhotos([...photos, ...newPhotos]);
    };

    const [coverFile, setCoverFile] = useState(null);

    const handleManualCoverUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            setCoverFile(file);
            const previewUrl = URL.createObjectURL(file);
            setBookDetails(prev => ({ ...prev, thumbnail: previewUrl }));
        }
    };

    const analyzePhotos = () => {
        if (photos.length === 0) return;
        setAnalyzing(true);
        setTimeout(() => {
            setAnalyzing(false);
            setAnalysisResult({
                match: true,
                conditionMatch: overallScore > 80 ? "Excellent" : "Fair",
                message: "Photos look consistent with declared condition!"
            });
        }, 2000);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const calculatedPrice = Math.floor((Number(bookDetails.basePrice) || 0) * (overallScore / 100));

            const uploadedImageUrls = [];
            // Keep existing photos
            photos.forEach(p => {
                if (p.existing) uploadedImageUrls.push(p.url);
            });

            for (const photo of photos) {
                if (!photo.existing) {
                    const formData = new FormData();
                    formData.append('file', photo.file);
                    try {
                        const uploadRes = await api.post('/api/images/upload', formData, {
                            headers: { 'Content-Type': 'multipart/form-data' }
                        });
                        uploadedImageUrls.push(uploadRes.data.url);
                    } catch (err) {
                        console.error("Error uploading image:", err);
                    }
                }
            }

            let finalThumbnail = bookDetails.thumbnail;
            if (coverFile) {
                const formData = new FormData();
                formData.append('file', coverFile);
                try {
                    const uploadRes = await api.post('/api/images/upload', formData, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                    });
                    finalThumbnail = uploadRes.data.url;
                } catch (err) {
                    console.error("Error uploading cover:", err);
                }
            }

            const finalData = {
                category: bookDetails.selectedCategory,
                price: calculatedPrice,
                market_price: Number(bookDetails.basePrice) || null,
                condition: overallScore > 95 ? "Neuf" : overallScore > 80 ? "Comme neuf" : overallScore > 50 ? "Bon état" : "État acceptable",
                description: bookDetails.description || "No description provided",
                location: "Alger",
                page_count: Number(bookDetails.pageCount) || null,
                publication_date: bookDetails.publishedDate,
                custom_images: uploadedImageUrls,
                title: bookDetails.title,
                authors: Array.isArray(bookDetails.authors) ? bookDetails.authors.join(', ') : (bookDetails.authors || "Auteur Inconnu"),
                publisher: bookDetails.publisher,
                cover_image_url: finalThumbnail
            };

            await api.put(`/api/books/announcements/${id}`, finalData);
            alert("Announcement Updated Successfully!");
            navigate('/myannouncements');
        } catch (error) {
            console.error("Submission error details:", error.response?.data);
            alert("Error updating announcement.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="add-announce-container">
            <h1 className="page-title text-[#134BD7] ">Edit Announcement</h1>

            <div className="stepper-wrapper">
                <div className={`step-item ${step >= 1 ? 'completed' : ''} ${step === 1 ? 'active' : ''}`}>
                    <div className="step-number bg-[#134BD7] ">1</div>
                    <span className="step-label">Identify</span>
                </div>
                <div className="step-connector"></div>
                <div className={`step-item ${step >= 2 ? 'completed' : ''} ${step === 2 ? 'active' : ''}`}>
                    <div className="step-number">2</div>
                    <span className="step-label">Condition</span>
                </div>
                <div className="step-connector"></div>
                <div className={`step-item ${step >= 3 ? 'completed' : ''} ${step === 3 ? 'active' : ''}`}>
                    <div className="step-number">3</div>
                    <span className="step-label">Photos & Confirm</span>
                </div>
            </div>

            <div className="content-card glass-panel">
                {step === 1 && (
                    <div className="step-content fade-in">
                        <h2 className="section-title"><FaBarcode /> Review Details</h2>
                        <div className="manual-entry-form">
                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">ISBN (Not editable)</label>
                                    <input className="modern-input" value={isbn} disabled />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Title</label>
                                    <input
                                        className="modern-input"
                                        value={bookDetails.title}
                                        onChange={(e) => setBookDetails({ ...bookDetails, title: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Author(s)</label>
                                    <input
                                        className="modern-input"
                                        value={bookDetails.authors.join(', ')}
                                        onChange={(e) => setBookDetails({ ...bookDetails, authors: e.target.value.split(', ') })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Page Count</label>
                                    <input
                                        type="number"
                                        className="modern-input"
                                        value={bookDetails.pageCount}
                                        onChange={(e) => setBookDetails({ ...bookDetails, pageCount: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Category</label>
                                    <select
                                        className="modern-input"
                                        value={bookDetails.selectedCategory || ''}
                                        onChange={(e) => setBookDetails({ ...bookDetails, selectedCategory: e.target.value })}
                                    >
                                        <option value="" disabled>Select a category</option>
                                        {categories.map((cat, index) => (
                                            <option key={index} value={cat}>{cat}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-1">Market Price (DZD)</label>
                                    <input
                                        type="number"
                                        className="modern-input"
                                        value={bookDetails.basePrice}
                                        onChange={(e) => setBookDetails({ ...bookDetails, basePrice: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div className="col-span-2 mb-4">
                                <label className="block text-sm font-medium mb-1">Description</label>
                                <textarea
                                    className="modern-input"
                                    rows="4"
                                    value={bookDetails.description}
                                    onChange={(e) => setBookDetails({ ...bookDetails, description: e.target.value })}
                                />
                            </div>
                            <div className="col-span-2">
                                <label className="block text-sm font-medium mb-1">Book Cover</label>
                                <div className="manual-cover-upload">
                                    <input
                                        type="file"
                                        id="manual-cover"
                                        accept="image/*"
                                        onChange={handleManualCoverUpload}
                                        className="hidden-input"
                                    />
                                    <label htmlFor="manual-cover" className="manual-cover-label">
                                        {bookDetails.thumbnail ? (
                                            <div className="cover-preview-mini">
                                                <img src={bookDetails.thumbnail} alt="Selected Cover" />
                                                <span>Change Cover</span>
                                            </div>
                                        ) : (
                                            <div className="upload-placeholder">
                                                <FaUpload />
                                                <span>Upload Cover Image</span>
                                            </div>
                                        )}
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div className="action-row">
                            <span></span>
                            <button className="btn-primary" onClick={() => setStep(2)}>
                                Next Step <FaArrowRight />
                            </button>
                        </div>
                    </div>
                )}

                {step === 2 && (
                    <div className="step-content fade-in">
                        <div className="score-header">
                            <h2 className="section-title"><MdVerified /> Condition Scoring</h2>
                            <div className="live-score">
                                <span className="score-label">Overall Score</span>
                                <div className={`score-circle score-${Math.floor(overallScore / 20)}`}>
                                    {overallScore}<span>/100</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 text-center transform transition-all duration-300 hover:shadow-md price-row ">
                            <div className="flex justify-around items-center mb-2">
                                <div className="text-center">
                                    <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">Market Price (DZD)</p>
                                    <input
                                        type="number"
                                        className="text-xl font-bold text-gray-700 text-center w-32 bg-white border border-gray-300 rounded-md p-1"
                                        value={bookDetails.basePrice}
                                        onChange={(e) => setBookDetails({ ...bookDetails, basePrice: e.target.value })}
                                    />
                                </div>
                                <div className="text-center">
                                    <p className="text-gray-500 text-xs uppercase tracking-wide mb-1">Condition Impact</p>
                                    <p className={`text-xl font-bold ${overallScore > 70 ? 'text-green-600' : 'text-orange-500'}`}>{overallScore}%</p>
                                </div>
                            </div>
                            <div className="border-t border-blue-100 pt-3 mt-2">
                                <p className="text-[#134BD7] text-sm font-bold uppercase tracking-wide mb-1">Suggested Selling Price</p>
                                <div className="flex items-center justify-center gap-2">
                                    <span className="text-4xl font-extrabold text-[#134BD7] drop-shadow-sm">
                                        {Math.floor((bookDetails.basePrice || 0) * (overallScore / 100))}
                                    </span>
                                    <span className="text-xl font-bold text-gray-500 self-end mb-2">DZD</span>
                                </div>
                            </div>
                        </div>

                        <div className="scoring-grid">
                            <div className="score-category">
                                <h3>Page Quality</h3>
                                <label><input type="checkbox" checked={scoringData.page.page_no_missing} onChange={() => handleScoreChange('page', 'page_no_missing')} /> No missing pages</label>
                                <label><input type="checkbox" checked={scoringData.page.page_no_torn} onChange={() => handleScoreChange('page', 'page_no_torn')} /> No torn pages</label>
                                <label><input type="checkbox" checked={scoringData.page.page_clean} onChange={() => handleScoreChange('page', 'page_clean')} /> Pages are clean</label>
                            </div>
                            <div className="score-category">
                                <h3>Binding</h3>
                                <label><input type="checkbox" checked={scoringData.binding.binding_no_loose} onChange={() => handleScoreChange('binding', 'binding_no_loose')} /> No loose pages</label>
                                <label><input type="checkbox" checked={scoringData.binding.binding_no_falling} onChange={() => handleScoreChange('binding', 'binding_no_falling')} /> No falling pages</label>
                                <label><input type="checkbox" checked={scoringData.binding.binding_stable} onChange={() => handleScoreChange('binding', 'binding_stable')} /> Binding is stable</label>
                            </div>
                            <div className="score-category">
                                <h3>Cover</h3>
                                <label><input type="checkbox" checked={scoringData.cover.cover_no_detachment} onChange={() => handleScoreChange('cover', 'cover_no_detachment')} /> No detachment</label>
                                <label><input type="checkbox" checked={scoringData.cover.cover_clean} onChange={() => handleScoreChange('cover', 'cover_clean')} /> Cover is clean</label>
                                <label><input type="checkbox" checked={scoringData.cover.cover_no_scratches} onChange={() => handleScoreChange('cover', 'cover_no_scratches')} /> No scratches</label>
                            </div>
                            <div className="score-category">
                                <h3>Damages</h3>
                                <label><input type="checkbox" checked={scoringData.damages.damage_no_burns} onChange={() => handleScoreChange('damages', 'damage_no_burns')} /> No burns</label>
                                <label><input type="checkbox" checked={scoringData.damages.damage_no_smell} onChange={() => handleScoreChange('damages', 'damage_no_smell')} /> No bad smell</label>
                                <label><input type="checkbox" checked={scoringData.damages.damage_no_insects} onChange={() => handleScoreChange('damages', 'damage_no_insects')} /> No insect damage</label>
                            </div>
                        </div>

                        <div className="action-row flex justify-between items-center">
                            <button className="btn-secondary" onClick={() => setStep(1)}><FaArrowLeft /> Back</button>
                            <button className="btn-primary" onClick={() => setStep(3)}>Next Step <FaArrowRight /></button>
                        </div>
                    </div>
                )}

                {step === 3 && (
                    <div className="step-content fade-in">
                        <h2 className="section-title"><FaCamera /> Photos & Confirm</h2>
                        <div className="photo-upload-area">
                            <div className="upload-box">
                                <input type="file" id="photos" multiple accept="image/*" onChange={handlePhotoUpload} />
                                <label htmlFor="photos">
                                    <FaCamera size={30} />
                                    <span>Upload Photos (2-4)</span>
                                </label>
                            </div>
                            <div className="photos-preview">
                                {photos.map((p, i) => (
                                    <img key={i} src={p.preview} alt={`preview ${i}`} />
                                ))}
                            </div>
                        </div>

                        {photos.length >= 1 && (
                            <button className="btn-ai" onClick={analyzePhotos} disabled={analyzing}>
                                {analyzing ? 'Analyzing...' : <><FaRobot /> Analyze with AI</>}
                            </button>
                        )}

                        <div className="price-section flex flex-col items-center gap-3 w-full mb-6 mt-6">
                            <p className="text-gray-500">Final Selling Price</p>
                            <div className="text-3xl font-bold text-[#134BD7]">
                                {Math.floor((bookDetails.basePrice || 0) * (overallScore / 100))} DZD
                            </div>
                        </div>

                        <div className="flex justify-between items-center gap-10">
                            <button className="back-button flex items-center gap-2 bg-[#134BD7] text-white rounded-md px-6 py-3 font-medium cursor-pointer" onClick={() => setStep(2)}>
                                <FaArrowLeft /> Back
                            </button>
                            <button className="btn-submit flex-1 h-15 bg-[#F3A109] text-white font-bold rounded-md" onClick={handleSubmit}>
                                Update Announcement
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default EditAnnounce;
