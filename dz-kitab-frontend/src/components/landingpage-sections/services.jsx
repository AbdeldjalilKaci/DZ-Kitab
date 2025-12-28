import React from 'react'
import { ServiceCard } from '../service-card'
import { useScrollAnimation } from '../../hooks/useScrollAnimation'

export const Services = () => {
    const titleRef = useScrollAnimation('fade-up', 0);
    const descRef = useScrollAnimation('fade-up', 100);
    const card1Ref = useScrollAnimation('fade-up', 200);
    const card2Ref = useScrollAnimation('fade-up', 350);
    const card3Ref = useScrollAnimation('fade-up', 500);

    return (
        <section id='services' className='services-section'>
            <h3 ref={titleRef}>Our <span>Services</span></h3>
            <p ref={descRef} className='p'>DZ-Kitab est une plateforme numérique dédiée aux livres en Algérie. L'objectif est de moderniser l'accès au livre et de connecter vendeurs, lecteurs et libraires.</p>
            <div className="services-cards">
                <div ref={card1Ref}>
                    <ServiceCard
                        service_image={'/service1.png'}
                        service_desc={"Vendez facilement vos livres et donnez-leur une seconde vie"}
                    />
                </div>
                <div ref={card2Ref}>
                    <ServiceCard
                        service_image={'/service2.png'}
                        service_desc={"Explorez de nouvelles œuvres et auteurs grâce à nos recommandations"}
                    />
                </div>
                <div ref={card3Ref}>
                    <ServiceCard
                        service_image={'/service3.png'}
                        service_desc={"Trouvez des livres neufs et d'occasion à des prix compétitifs partout en Algérie"}
                    />
                </div>
            </div>
        </section>
    )
}
