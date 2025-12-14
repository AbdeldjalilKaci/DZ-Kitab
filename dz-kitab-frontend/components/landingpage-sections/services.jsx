import React from 'react'
import { ServiceCard } from '../service-card'

export const Services = () => {
    return (
        <section className='services-section'>
            <h3>Our <span>Services</span></h3>
            <p className='p'>DZ-Kitab est une plateforme numérique dédiée aux livres en Algérie. L'objectif est de moderniser l'accès au livre et de connecter vendeurs, lecteurs et libraires.</p>
            <div className="services-cards">
                <ServiceCard
                    service_icon={'🛒'}
                    service_title={'Acheter des livres'}
                    service_desc={"Trouvez des livres neufs et d'occasion à des prix compétitifs partout en Algérie"}
                />
                <ServiceCard
                    service_icon={'💰'}
                    service_title={'Vendre vos livres'}
                    service_desc={"Vendez facilement vos livres et donnez-leur une seconde vie"}
                />
                <ServiceCard
                    service_icon={'🔍'}
                    service_title={'Découvrir'}
                    service_desc={"Explorez de nouvelles œuvres et auteurs grâce à nos recommandations"}
                />
            </div>
        </section>
    )
}
