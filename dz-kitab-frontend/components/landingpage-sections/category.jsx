import React from 'react'
import { CategoryCard } from '../category-card'

export const Category = () => {
    return (
        <section className='category-section'>
            <h3>Browser by <span>Book Types</span></h3>
            <div className="categorys">
                <CategoryCard title={'Math Books'} image={'./ai2.jpg'}  />
                <CategoryCard title={'Math Books'} image={'./math2.jpg'}  />
                <CategoryCard title={'Math Books'} image={'./ai2.jpg'}  />
                <CategoryCard title={'Math Books'} image={'./ai2.jpg'}  />
                <CategoryCard title={'Math Books'} image={'./ai2.jpg'}  />
                <CategoryCard title={'Math Books'} image={'./ai2.jpg'}  />
                <CategoryCard title={'Math Books'} image={'./ai2.jpg'}  />
                <CategoryCard title={'Math Books'} image={'./ai2.jpg'}  />
            </div>
        </section>
    )
}
