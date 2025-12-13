import React from 'react'
import { BookCard } from '../book-card'
export const Books = () => {
    return (
        <section className='popular-books'>
            <h3>Populaire <span>Books</span></h3>
            <div className="books-div">
                <BookCard
                    img={'./ai.png'}
                    title={'Artificial Intelligence'}
                    desc={"Trouvez des livres neufs et d'occasion à des prix compétitifs partout en Algérie"}
                    price={'100 DA'}
                />
                <BookCard
                    img={'./yourbook.png'}
                    title={'YOUR BOOK TITLE'}
                    desc={"Trouvez des livres neufs et d'occasion à des prix compétitifs partout en Algérie"}
                    price={'1500 DA'}
                />
                <BookCard
                    img={'./math.png'}
                    title={'MATHS'}
                    desc={"Trouvez des livres neufs et d'occasion à des prix compétitifs partout en Algérie"}
                    price={'3000 DA'}
                />
                <BookCard
                    img={'./math.png'}
                    title={'MATHS'}
                    desc={"Trouvez des livres neufs et d'occasion à des prix compétitifs partout en Algérie"}
                    price={'3000 DA'}
                />
            </div>
        </section>
    )
}
