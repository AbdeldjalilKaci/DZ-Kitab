import React from 'react'
import { CiSearch } from "react-icons/ci";
export const Hero = () => {
    return (
        <section className='hero'>
            <div className="hero-info">
                <h3>
                    DZ-Kitab – La Révolution <span>du Livre en Algérie</span>
                </h3>
                <p className='p'> La plateforme où les étudiants achètent et vendent leurs manuels. Économisez jusqu'à 70% sur vos livres de cours.</p>
                <div className="search">
                    <input type='search' placeholder='Search...' className='search-input'></input>
                    <button className="search-button">
                        <p>Find Book</p>
                        <CiSearch />
                    </button>
                </div>
            </div>
            <div className="herocover">
                <img className='heropicture' src='./heropicture.png'></img>
            </div>
        </section>
    )
}
