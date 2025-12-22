import React from 'react'
import { ServiceCard } from '../service-card'

export const Services = () => {
    return (
        <section id='services' className='services-section'>
            <h3>Our <span>Services</span></h3>
            <p className='p'>DZ-Kitab est une plateforme numérique dédiée aux livres en Algérie. L'objectif est de moderniser l'accès au livre et de connecter vendeurs, lecteurs et libraires.</p>
            <div className="services-cards">
                <ServiceCard
                    service_image={'/service1.png'}
                    service_desc={"Vendez facilement vos livres et donnez-leur une seconde vie"}
                />
                <ServiceCard
                    service_image={'/service2.png'}
                    service_desc={"Explorez de nouvelles œuvres et auteurs grâce à nos recommandations"}
                />
                <ServiceCard
                    service_image={'/service3.png'}
                    service_desc={"Trouvez des livres neufs et d'occasion à des prix compétitifs partout en Algérie"}
                />
            </div>
        </section>
    )
}
