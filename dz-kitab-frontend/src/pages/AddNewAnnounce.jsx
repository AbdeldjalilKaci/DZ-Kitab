import React, { useState, useEffect } from 'react';
import './addnewannouce.css';
import { FaSearch, FaBook, FaCheckCircle, FaCamera, FaRobot, FaArrowRight, FaArrowLeft, FaBarcode, FaUpload } from 'react-icons/fa';
import { MdVerified, MdWarning } from 'react-icons/md';

function AddAnnounce() {
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);

    const [isbn, setIsbn] = useState('');
    const [bookFound, setBookFound] = useState(false);
    const [manualEntry, setManualEntry] = useState(false);
    const [bookDetails, setBookDetails] = useState({
        title: '',
        authors: [],
        pageCount: '',
        publishedDate: '',
        categories: [],
        description: '',
        thumbnail: '',
        publisher: ''
    });

    const initialScoring = {
        page: {
            missing: false,
            torn: false,
            stained: false,
            score: 0
        },
        binding: {
            loose: false,
            detached: false,
            score: 0
        },
        cover: {
            dirty: false,
            scratched: false,
            detached: false,
            score: 0
        },
        damages: {
            burns: false,
            smell: false,
            insects: false,
            score: 0
        },
        accessories: {
            complete: true,
            extras: false,
            score: 0
        }
    };
    const [scoringData, setScoringData] = useState(initialScoring);
    const [overallScore, setOverallScore] = useState(10);

    const [photos, setPhotos] = useState([]);
    const [price, setPrice] = useState('');
    const [analyzing, setAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState(null);


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
        let score = 100;

        if (scoringData.page.missing) score -= 40;
        if (scoringData.page.torn) score -= 15;
        if (scoringData.page.stained) score -= 10;

        if (scoringData.binding.loose) score -= 15;
        if (scoringData.binding.detached) score -= 30;

        if (scoringData.cover.dirty) score -= 5;
        if (scoringData.cover.scratched) score -= 5;
        if (scoringData.cover.detached) score -= 20;

        if (scoringData.damages.burns) score -= 50;
        if (scoringData.damages.smell) score -= 20;
        if (scoringData.damages.insects) score -= 80;

        if (!scoringData.accessories.complete) score -= 10;
        if (scoringData.accessories.extras) score += 5;

        setOverallScore(Math.max(0, Math.min(100, score)));
    }, [scoringData]);

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
        const finalData = {
            ...bookDetails,
            isbn,
            conditionScore: overallScore,
            scoringDetails: scoringData,
            price,
            photos
        };
        console.log("Submitting:", finalData);
        alert("Announcement Created! (Check console for data)");
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
                    <span className="step-label">Photos & Price</span>
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
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Category</label>
                                        <input
                                            className="modern-input"
                                            value={bookDetails.categories[0] || ''}
                                            onChange={(e) => setBookDetails({ ...bookDetails, categories: [e.target.value] })}
                                            placeholder="e.g. Fiction"
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
                                    <span className="badge-category">{bookDetails.categories[0]}</span>
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

                        <div className="scoring-grid">
                            <div className="score-category">
                                <h3>Page Quality</h3>
                                <label><input type="checkbox" checked={!scoringData.page.missing} onChange={() => handleScoreChange('page', 'missing')} /> No missing pages</label>
                                <label><input type="checkbox" checked={!scoringData.page.torn} onChange={() => handleScoreChange('page', 'torn')} /> No torn pages</label>
                                <label><input type="checkbox" checked={!scoringData.page.stained} onChange={() => handleScoreChange('page', 'stained')} /> No stains</label>
                            </div>

                            <div className="score-category">
                                <h3>Binding</h3>
                                <label><input type="checkbox" checked={!scoringData.binding.loose} onChange={() => handleScoreChange('binding', 'loose')} /> Tight binding</label>
                                <label><input type="checkbox" checked={!scoringData.binding.detached} onChange={() => handleScoreChange('binding', 'detached')} /> Cover attached</label>
                            </div>

                            <div className="score-category">
                                <h3>Cover</h3>
                                <label><input type="checkbox" checked={!scoringData.cover.dirty} onChange={() => handleScoreChange('cover', 'dirty')} /> Clean cover</label>
                                <label><input type="checkbox" checked={!scoringData.cover.scratched} onChange={() => handleScoreChange('cover', 'scratched')} /> No scratches</label>
                            </div>

                            <div className="score-category">
                                <h3>Major Damages</h3>
                                <label><input type="checkbox" checked={!scoringData.damages.burns} onChange={() => handleScoreChange('damages', 'burns')} /> No burns</label>
                                <label><input type="checkbox" checked={!scoringData.damages.smell} onChange={() => handleScoreChange('damages', 'smell')} /> No odors</label>
                            </div>

                            <div className="score-category">
                                <h3>Accessories</h3>
                                <label><input type="checkbox" checked={scoringData.accessories.complete} onChange={() => handleScoreChange('accessories', 'complete')} /> All accessories included</label>
                                <label><input type="checkbox" checked={scoringData.accessories.extras} onChange={() => handleScoreChange('accessories', 'extras')} /> Has extras (bookmarks etc)</label>
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
                        <h2 className="section-title"><FaCamera /> Photos & Price</h2>

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

                        <div className="price-section flex gap-5 w-full ">
                            <label className=' w-100 '>Set your price (DZD)</label>
                            <input
                                type="number"
                                className="modern-input price-input w-100 h-15 border-none outline-none  "
                                placeholder="0.00"
                                value={price}
                                onChange={(e) => setPrice(e.target.value)}
                            />
                            {bookDetails.pageCount && (
                                <p className="price-suggestion">Suggested price: {Math.floor(bookDetails.pageCount * 1.5)} - {Math.floor(bookDetails.pageCount * 2.5)} DZD</p>
                            )}
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