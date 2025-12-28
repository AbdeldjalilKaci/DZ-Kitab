import React, { useState, useEffect, useRef } from 'react'
import { CiSearch } from "react-icons/ci";
import { useNavigate } from 'react-router-dom';

export const Hero = ({ isLoggedIn }) => {
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState('');
    const titleRef = useRef(null);
    const descRef = useRef(null);
    const buttonRef = useRef(null);

    useEffect(() => {
        // Animate on mount
        if (titleRef.current) {
            titleRef.current.style.opacity = '0';
            titleRef.current.style.transform = 'translateY(30px)';
            setTimeout(() => {
                titleRef.current.style.transition = 'opacity 1s ease-out, transform 1s ease-out';
                titleRef.current.style.opacity = '1';
                titleRef.current.style.transform = 'translateY(0)';
            }, 100);
        }
        if (descRef.current) {
            descRef.current.style.opacity = '0';
            descRef.current.style.transform = 'translateY(30px)';
            setTimeout(() => {
                descRef.current.style.transition = 'opacity 1s ease-out 0.3s, transform 1s ease-out 0.3s';
                descRef.current.style.opacity = '1';
                descRef.current.style.transform = 'translateY(0)';
            }, 100);
        }
        if (buttonRef.current) {
            buttonRef.current.style.opacity = '0';
            buttonRef.current.style.transform = 'translateY(30px)';
            setTimeout(() => {
                buttonRef.current.style.transition = 'opacity 1s ease-out 0.6s, transform 1s ease-out 0.6s';
                buttonRef.current.style.opacity = '1';
                buttonRef.current.style.transform = 'translateY(0)';
            }, 100);
        }
    }, []);

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            navigate(`/catalog?search=${encodeURIComponent(searchQuery)}`);
        }
    };

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
                <h3 ref={titleRef} className='text-white text-3xl md:text-5xl font-bold mb-4 max-w-2xl'>
                    DZ-Kitab – La Révolution du Livre en Algérie
                </h3>
                <p ref={descRef} className='text-gray-200 text-lg md:text-xl w-full max-w-xl mb-8 leading-relaxed'>
                    La plateforme où les étudiants achètent et vendent leurs manuels. Économisez jusqu'à 70% sur vos livres de cours.
                </p>

                <a href='#services' ref={buttonRef}>
                    <button className='' >
                        View More
                    </button>
                </a>
            </div>
        </section>
    )
}
