import React, { useEffect, useState } from 'react'
import { BookCard } from '../book-card'
import api from '../../utils/api'
import { useNavigate } from 'react-router-dom'
import { useScrollAnimation } from '../../hooks/useScrollAnimation'

const AnimatedBookCard = ({ ann, index, navigate, truncateText }) => {
    const cardRef = useScrollAnimation(
        index % 2 === 0 ? 'fade-right' : 'fade-left',
        index * 150
    );

    return (
        <div ref={cardRef}>
            <BookCard
                id={ann.id}
                img={ann.book.cover_image_url || 'https://via.placeholder.com/150'}
                title={ann.book.title}
                desc={truncateText(ann.description)}
                price={`${ann.price} DA`}
                buy_func={() => navigate(`/book/${ann.id}`)}
            />
        </div>
    );
};

export const Books = () => {
    const [announcements, setAnnouncements] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    const titleRef = useScrollAnimation('fade-up', 0);

    const truncateText = (text, maxLength = 50) => {
        if (!text) return "Pas de description";
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + "...";
    };

    useEffect(() => {
        const fetchPopular = async () => {
            try {
                const res = await api.get('/api/books/announcements?limit=4');
                setAnnouncements(res.data.announcements);
            } catch (err) {
                console.error("Error fetching popular books:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchPopular();
    }, []);

    return (
        <section className='popular-books'>
            <h3 ref={titleRef}>Populaire <span>Books</span></h3>
            <div className="books-div">
                {loading ? (
                    <p>Loading...</p>
                ) : announcements.length > 0 ? (
                    announcements.map((ann, index) => (
                        <AnimatedBookCard
                            key={ann.id}
                            ann={ann}
                            index={index}
                            navigate={navigate}
                            truncateText={truncateText}
                        />
                    ))
                ) : (
                    <p>Aucune annonce disponible pour le moment.</p>
                )}
            </div>
        </section>
    )
}

