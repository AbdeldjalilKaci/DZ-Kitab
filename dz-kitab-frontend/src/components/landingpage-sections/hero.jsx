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
            {/* Black overlay */}
            <div className="absolute inset-0 bg-black/40"></div>
            <div className="hero-info z-50 ">
                <h3 className=' text-white' >
                    DZ-Kitab – La Révolution du Livre en Algérie
                </h3>
                <p className='text-gray-200 w-120 '> La plateforme où les étudiants achètent et vendent leurs manuels. Économisez jusqu'à 70% sur vos livres de cours.</p>
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
