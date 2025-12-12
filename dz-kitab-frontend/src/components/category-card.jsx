import React from "react";

export const CategoryCard = ({ title, image, side }) => {
    return (
        <div className="category-card">
            <div className="card-bg" style={{ backgroundImage: `url(${image})` }}></div>
            <div className="card-overlay"></div>
            <div className="card-content">
                <p>{title}</p>
            </div>
        </div>
    );
};
