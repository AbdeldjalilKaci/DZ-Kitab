import React from 'react'
import { CiSearch } from "react-icons/ci";
export const Hero = () => {
    return (
        <section
            style={{
                backgroundImage: "url('/herophoto.png')",
                backgroundSize: "cover",
                backgroundPosition: "center",
                backgroundRepeat: "no-repeat",
            }}
            className="relative hero min-h-[500px] w-full"
        >
            <div className="absolute inset-0 bg-black/40"></div>
            <div className="hero-info z-50 ">
                <h3 className='text-white text-3xl md:text-5xl font-bold mb-4 max-w-2xl'>
                    DZ-Kitab – La Révolution du Livre en Algérie
                </h3>
                <p className='text-gray-200 text-lg md:text-xl w-full max-w-xl mb-8 leading-relaxed'>
                    La plateforme où les étudiants achètent et vendent leurs manuels. Économisez jusqu'à 70% sur vos livres de cours.
                </p>
                {/* <div className="search">
                    <input type='search' placeholder='Search...' className='search-input'></input>
                    <button className="search-button">
                        <p>Find Book</p>
                        <CiSearch />
                    </button>
                </div> */}

                <a href='#services' >
                    <button className='' >
                        View More
                    </button>
                </a>
            </div>
            {/* <div className="herocover">
                <img className='heropicture' src='./heropicture.png'></img>
            </div> */}
        </section>
    )
}
