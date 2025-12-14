import React from 'react'
import { Hero } from '../components/landingpage-sections/hero'
import { Services } from '../components/landingpage-sections/services'
import { Books } from '../components/landingpage-sections/books'
import { Category } from '../components/landingpage-sections/category'
export const Landingpage = () => {
    return (
        <div className="">
            <Hero/> 
            <Services/>
            <Books/>
            <Category/>
        </div>
    )
}
