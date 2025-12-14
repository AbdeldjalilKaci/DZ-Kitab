import React from 'react'

export const ServiceCard = ({ service_icon, service_title, service_desc }) => {
    return (
        <div className="service-card">
            <div className="content">
                <p className='icon'>{service_icon}</p>
                <h4>{service_title}</h4>
                <p className='desc'>{service_desc}</p>
            </div>
        </div>

    )
}
