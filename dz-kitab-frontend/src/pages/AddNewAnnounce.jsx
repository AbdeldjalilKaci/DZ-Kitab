import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './addnewannouce.css';
import { FaSearch, FaBook, FaCheckCircle, FaCamera, FaRobot, FaArrowRight, FaArrowLeft, FaBarcode, FaUpload } from 'react-icons/fa';
import { MdVerified, MdWarning } from 'react-icons/md';

function AddAnnounce() {
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
        basePrice: ''
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
    const [price, setPrice] = useState('');
    const [analyzing, setAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState(null);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const response = await axios.get('http://localhost:8000/categories');
                setCategories(response.data);
            } catch (error) {
                console.error("Error fetching categories:", error);
            }
        };
        fetchCategories();
    }, []);

    const fetchBookDetails = async () => {
        if (!isbn) return;
        setLoading(true);
        try {
            const response = await fetch(`https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}`);
            const data = await response.json();
            if (data.items && data.items.length > 0) {
                const info = data.items[0].volumeInfo;
                setBookDetails({
                    title: info.title || '',
                    authors: info.authors || [],
                    pageCount: info.pageCount || '',
                    publishedDate: info.publishedDate || '',
                    categories: info.categories || [],
                    description: info.description || '',
                    thumbnail: info.imageLinks?.thumbnail || '',
                    publisher: info.publisher || ''
                });
                setBookFound(true);
            } else {
                alert('Book not found! Please enter details manually.');
                setBookFound(false);
            }
        } catch (error) {
            console.error(error);
            alert('Error fetching book details.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const isStateValid = scoringData?.page && 'page_no_missing' in scoringData.page;
        if (!isStateValid) {
            console.log("Resetting state due to schema mismatch");
            setScoringData(initialScoring);
        }
    }, [scoringData]);

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

        if (
            scoringData.page.page_score !== pScore ||
            scoringData.binding.binding_score !== bScore ||
            scoringData.cover.cover_score !== cScore ||
            scoringData.damages.damage_score !== dScore ||
            scoringData.accessories.accessories_score !== aScore ||
            overallScore !== newOverall
        ) {
            setScoringData(prev => ({
                ...prev,
                page: { ...prev.page, page_score: pScore },
                binding: { ...prev.binding, binding_score: bScore },
                cover: { ...prev.cover, cover_score: cScore },
                damages: { ...prev.damages, damage_score: dScore },
                accessories: { ...prev.accessories, accessories_score: aScore }
            }));
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

    const handleManualCoverUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
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

    const handleSubmit = (e) => {
        e.preventDefault();
        const calculatedPrice = Math.floor((bookDetails.basePrice || 0) * (overallScore / 100));
        const finalData = {
            ...bookDetails,
            isbn,
            conditionScore: overallScore,
            scoringDetails: scoringData,
            price: calculatedPrice,
            photos
        };
        console.log("Submitting:", finalData);
        alert(`Announcement Created for ${calculatedPrice} DZD! (Check console for data)`);
    };


    return (
        <div className="add-announce-container">
            <h1 className="page-title text-[#134BD7] ">Sell Your Book</h1>

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
                        <h2 className="section-title"><FaBarcode /> Identify Book</h2>

                        {!manualEntry ? (
                            <>
                                <div className="isbn-search-box">
                                    <input
                                        type="text"
                                        placeholder="Enter ISBN (e.g. 9780134685991)"
                                        value={isbn}
                                        onChange={(e) => setIsbn(e.target.value)}
                                        className="modern-input"
                                    />
                                    <button onClick={fetchBookDetails} disabled={loading} className="btn-primary search-btn">
                                        {loading ? 'Searching...' : <><FaSearch /> Search</>}
                                    </button>
                                </div>
                                <p className="hint-text">Enter ISBN to auto-fill details (Google Books API)</p>

                                <div className="manual-entry-link">
                                    <span onClick={() => setManualEntry(true)} className="text-[#134BD7] cursor-pointer underline">
                                        Book not found? Enter manually
                                    </span>
                                </div>
                            </>
                        ) : (
                            <div className="manual-entry-form">
                                <h3 className="text-lg font-semibold mb-4">Manual Entry</h3>
                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-1">ISBN</label>
                                        <input
                                            className="modern-input"
                                            value={isbn}
                                            onChange={(e) => setIsbn(e.target.value)}
                                            placeholder="ISBN"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Title</label>
                                        <input
                                            className="modern-input"
                                            value={bookDetails.title}
                                            onChange={(e) => setBookDetails({ ...bookDetails, title: e.target.value })}
                                            placeholder="Book Title"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Author(s)</label>
                                        <input
                                            className="modern-input"
                                            value={bookDetails.authors.join(', ')}
                                            onChange={(e) => setBookDetails({ ...bookDetails, authors: e.target.value.split(', ') })}
                                            placeholder="Authors (comma separated)"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Page Count</label>
                                        <input
                                            type="number"
                                            className="modern-input"
                                            value={bookDetails.pageCount}
                                            onChange={(e) => setBookDetails({ ...bookDetails, pageCount: e.target.value })}
                                            placeholder="e.g. 300"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Category</label>
                                        <select
                                            className="modern-input"
                                            value={bookDetails.categories[0] || ''}
                                            onChange={(e) => setBookDetails({ ...bookDetails, categories: [e.target.value] })}
                                        >
                                            <option value="" disabled>Select a category</option>
                                            {categories.map((cat, index) => (
                                                <option key={index} value={cat.name || cat}>{cat.name || cat}</option>
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
                                            placeholder="e.g. 1500"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Publication Date</label>
                                        <input
                                            type="date"
                                            className="modern-input"
                                            value={bookDetails.publishedDate}
                                            onChange={(e) => setBookDetails({ ...bookDetails, publishedDate: e.target.value })}
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
                                <button onClick={() => setManualEntry(false)} className="text-sm text-gray-500 underline mb-4">
                                    Back to ISBN Search
                                </button>
                            </div>
                        )}

                        {bookDetails.title && !manualEntry && (
                            <div className="book-preview-card">
                                {bookDetails.thumbnail && <img src={bookDetails.thumbnail} alt="Cover" className="book-cover-preview" />}
                                <div className="book-info-preview">
                                    <h3>{bookDetails.title}</h3>
                                    <p><strong>Author:</strong> {bookDetails.authors.join(', ')}</p>
                                    <p><strong>Publisher:</strong> {bookDetails.publisher} ({bookDetails.publishedDate})</p>
                                    <p><strong>Pages:</strong> {bookDetails.pageCount}</p>
                                    <div className="mt-2">
                                        <label className="block text-sm font-medium mb-1 text-gray-700">Market Price (DZD)</label>
                                        <input
                                            type="number"
                                            className="modern-input"
                                            value={bookDetails.basePrice || ''}
                                            onChange={(e) => setBookDetails({ ...bookDetails, basePrice: e.target.value })}
                                            placeholder="Enter market price"
                                            required
                                        />
                                    </div>
                                    <span className="badge-category mt-2">{bookDetails.categories[0]}</span>
                                </div>
                            </div>
                        )}

                        <div className="action-row">
                            <span></span>
                            <button
                                className="btn-primary"
                                onClick={() => setStep(2)}
                                disabled={!bookDetails.title && !bookFound && !manualEntry}
                            >
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
                                        placeholder="0"
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
                                <p className="text-xs text-gray-400 mt-1">based on market price & condition</p>
                            </div>
                        </div>

                        <div className="scoring-grid">
                            <div className="score-category">
                                <div className="mb-2">
                                    <h3>Page Quality</h3>
                                </div>
                                <label><input type="checkbox" checked={scoringData.page.page_no_missing} onChange={() => handleScoreChange('page', 'page_no_missing')} /> No missing pages</label>
                                <label><input type="checkbox" checked={scoringData.page.page_no_torn} onChange={() => handleScoreChange('page', 'page_no_torn')} /> No torn pages</label>
                                <label><input type="checkbox" checked={scoringData.page.page_clean} onChange={() => handleScoreChange('page', 'page_clean')} /> Pages are clean</label>
                            </div>

                            <div className="score-category">
                                <div className="mb-2">
                                    <h3>Binding</h3>
                                </div>
                                <label><input type="checkbox" checked={scoringData.binding.binding_no_loose} onChange={() => handleScoreChange('binding', 'binding_no_loose')} /> No loose pages</label>
                                <label><input type="checkbox" checked={scoringData.binding.binding_no_falling} onChange={() => handleScoreChange('binding', 'binding_no_falling')} /> No falling pages</label>
                                <label><input type="checkbox" checked={scoringData.binding.binding_stable} onChange={() => handleScoreChange('binding', 'binding_stable')} /> Binding is stable</label>
                            </div>

                            <div className="score-category">
                                <div className="mb-2">
                                    <h3>Cover</h3>
                                </div>
                                <label><input type="checkbox" checked={scoringData.cover.cover_no_detachment} onChange={() => handleScoreChange('cover', 'cover_no_detachment')} /> No detachment</label>
                                <label><input type="checkbox" checked={scoringData.cover.cover_clean} onChange={() => handleScoreChange('cover', 'cover_clean')} /> Cover is clean</label>
                                <label><input type="checkbox" checked={scoringData.cover.cover_no_scratches} onChange={() => handleScoreChange('cover', 'cover_no_scratches')} /> No scratches</label>
                            </div>

                            <div className="score-category">
                                <div className="mb-2">
                                    <h3>Damages</h3>
                                </div>
                                <label><input type="checkbox" checked={scoringData.damages.damage_no_burns} onChange={() => handleScoreChange('damages', 'damage_no_burns')} /> No burns</label>
                                <label><input type="checkbox" checked={scoringData.damages.damage_no_smell} onChange={() => handleScoreChange('damages', 'damage_no_smell')} /> No bad smell</label>
                                <label><input type="checkbox" checked={scoringData.damages.damage_no_insects} onChange={() => handleScoreChange('damages', 'damage_no_insects')} /> No insect damage</label>
                            </div>

                            <div className="score-category">
                                <div className="mb-2">
                                    <h3>Accessories</h3>
                                </div>
                                <label><input type="checkbox" checked={scoringData.accessories.accessories_complete} onChange={() => handleScoreChange('accessories', 'accessories_complete')} /> Accessories complete</label>
                                <label><input type="checkbox" checked={scoringData.accessories.accessories_content} onChange={() => handleScoreChange('accessories', 'accessories_content')} /> Content intact</label>
                                <label><input type="checkbox" checked={scoringData.accessories.accessories_extras} onChange={() => handleScoreChange('accessories', 'accessories_extras')} /> Has extras</label>
                            </div>
                        </div>

                        <div className="action-row flex justify-between items-center  ">
                            <button className="btn-secondary" onClick={() => setStep(1)}><FaArrowLeft /> Back</button>
                            <button className="btn-primary" onClick={() => setStep(3)}>Next Step <FaArrowRight /></button>
                        </div>
                    </div>
                )}

                {step === 3 && (
                    <div className="step-content fade-in">
                        <h2 className="section-title"><FaCamera /> Photos & Confirm</h2>

                        <div className="ia-promo">
                            <FaRobot className="ia-icon" />
                            <div>
                                <h4>AI Analysis Available</h4>
                                <p>Ads with verified AI analysis sell 3x faster!</p>
                            </div>
                        </div>

                        <div className="photo-upload-area">
                            <div className="upload-box">
                                <input type="file" id="photos" multiple accept="image/*" onChange={handlePhotoUpload} />
                                <label htmlFor="photos">
                                    <FaCamera size={30} />
                                    <span>Click to upload (2-4 photos)</span>
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

                        {analysisResult && (
                            <div className="ai-result success">
                                <MdVerified /> {analysisResult.message}
                            </div>
                        )}

                        <div className="price-section flex flex-col items-center gap-3 w-full mb-6">
                            <p className="text-gray-500">Final Selling Price</p>
                            <div className="text-3xl font-bold text-[#134BD7]">
                                {Math.floor((bookDetails.basePrice || 0) * (overallScore / 100))} DZD
                            </div>
                            <p className="text-sm text-gray-400">Calculated from Market Price ({bookDetails.basePrice} DZD) & Condition ({overallScore}%)</p>
                        </div>

                        <div className="  flex justify-between items-center gap-10  ">
                            <button className=" back-button flex items-center gap-2 bg-[#134BD7] text-white rounded-md w-50 h-15 font-medium cursor-pointer " onClick={() => setStep(2)}><FaArrowLeft /> Back</button>
                            <button className="btn-submit w-100 h-15 bg-[#F3A109] " onClick={handleSubmit}>Publish Announcement</button>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
}

export default AddAnnounce;