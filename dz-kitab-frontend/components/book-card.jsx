import React from 'react'

export const BookCard = ({img,title,desc,price,buy_func}) => {
    return (
        <div className="book-card">
            <div className="book-cover">
                <img className='book-img' src={img} alt="" />
            </div>
            <h4>{title}</h4>
            <p className='book-desc'>{desc}</p>
            <hr></hr>
            <div className="buy-book">
                <p>{price}</p>
                <button className='buy-button' onClick={buy_func} >Buy Now</button>
            </div>
        </div>
    )
}
