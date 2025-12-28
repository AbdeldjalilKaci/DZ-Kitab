import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { CategoryCard } from '../category-card'
import api from '../../utils/api'

export const Category = () => {
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);

    // Map categories to appropriate Unsplash images
    const getCategoryImage = (category) => {
        const imageMap = {
            'Informatique': 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=800&q=80',
            'Mathématiques': 'https://images.unsplash.com/photo-1509228468518-180dd4864904?w=800&q=80',
            'Physique': 'https://images.unsplash.com/photo-1636466497217-26a8cbeaf0aa?w=800&q=80',
            'Chimie': 'https://images.unsplash.com/photo-1532634733-cae1395e440f?w=800&q=80',
            'Biologie': 'https://images.unsplash.com/photo-1530026405186-ed1f139313f8?w=800&q=80',
            'Médecine': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80',
            'Économie': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80',
            'Gestion': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&q=80',
            'Droit': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&q=80',
            'Langues': 'https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=800&q=80',
            'Littérature': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800&q=80',
            'Histoire': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=800&q=80',
            'Géographie': 'https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=800&q=80',
            'Philosophie': 'https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=800&q=80',
            'Psychologie': 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&q=80',
            'Architecture': 'https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=800&q=80',
            'Ingénierie': 'https://images.unsplash.com/photo-1581092795360-fd1ca04f0952?w=800&q=80',
            'Autre': 'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=800&q=80'
        };
        return imageMap[category] || 'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=800&q=80';
    };

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const response = await api.get('/api/books/categories');
                setCategories(response.data);
            } catch (error) {
                console.error("Error fetching categories:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchCategories();
    }, []);

    if (loading) {
        return (
            <section className="category-section">
                <h3>Browse by <span>Book Types</span></h3>
                <div className="categorys">
                    <p>Loading categories...</p>
                </div>
            </section>
        );
    }

    return (
        <section className="category-section">
            <h3>Browse by <span>Book Types</span></h3>

            <div className="flex gap-10 flex-wrap items-center">
                {categories.map((category, index) => (
                    <Link
                        key={index}
                        to={`/listing?category=${encodeURIComponent(category)}`}
                        style={{ textDecoration: 'none' }}
                    >
                        <CategoryCard
                            title={category}
                            image={getCategoryImage(category)}
                        />
                    </Link>
                ))}
            </div>
        </section>
    )
}
