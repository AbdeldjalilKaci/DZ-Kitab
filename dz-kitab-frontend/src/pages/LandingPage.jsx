import React from 'react'
import { Hero } from '../components/landingpage-sections/hero'
import { Services } from '../components/landingpage-sections/services'
import { Books } from '../components/landingpage-sections/books'
import { Category } from '../components/landingpage-sections/category'
import { getCookie } from '../utils/cookies'

export const Landingpage = () => {

    const token = getCookie("access_token");
    const isLoggedIn = !!token;


    return (
        <div className="">
            <Hero isLoggedIn={isLoggedIn} />
            <Services />
            <Books />
            <Category />
        </div>
    )
}

