import React from 'react'

export const ServiceCard = ({ service_image, service_desc }) => {
    return (
        <div className="service-card">
            <div className="service-image-wrapper">
                <img src={service_image} alt="Service" className="service-image" />
            </div>
            <p className='service-desc'>{service_desc}</p>
        </div>
    )
}
