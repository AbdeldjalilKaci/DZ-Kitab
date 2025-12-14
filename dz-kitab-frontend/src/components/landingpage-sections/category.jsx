import React from 'react'
import { CategoryCard } from '../category-card'

export const Category = () => {
    const categories = [
        'Math Books',
        'AI Books',
        'Science Books',
        'Medical Books',
        'Business Books',
        'Arabic Books'
    ]

    return (
        <section className="category-section">
            <h3>Browse by <span>Book Types</span></h3>

            <div className="categorys">
                {categories.map((category, index) => (
                        <CategoryCard
                            key={index}
                            title={category}
                            image="./ai2.jpg"
                        />
                ))}
            </div>
        </section>
    )
}
