import React, { useState, useEffect } from "react";
import api from "../utils/api";
import "./Community.css";

const Community = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const response = await api.get("/api/public/users");
                setUsers(response.data);
                setLoading(false);
            } catch (err) {
                console.error("Error fetching community users:", err);
                setError("Could not load community members.");
                setLoading(false);
            }
        };
        fetchUsers();
    }, []);

    if (loading) {
        return (
            <div className="community-container">
                <div className="loading-spinner">Loading our community...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="community-container">
                <div className="error-message">{error}</div>
            </div>
        );
    }

    return (
        <div className="community-page">
            <div className="community-hero">
                <h1>Our Community</h1>
                <p>Meet the students and members of DZ-Kitab at ESTIN and beyond.</p>
            </div>

            <div className="community-grid">
                {users.map((user) => (
                    <div key={user.id} className="user-card">
                        <div className="user-avatar">
                            {user.profile_picture_url ? (
                                <img src={user.profile_picture_url} alt={user.username} />
                            ) : (
                                <div className="avatar-placeholder">
                                    {user.first_name ? user.first_name.charAt(0) : user.username.charAt(0)}
                                </div>
                            )}
                        </div>
                        <div className="user-info">
                            <h3>{user.first_name} {user.last_name}</h3>
                            <p className="username">@{user.username}</p>
                            <div className="user-badge">{user.university || "Academic Member"}</div>
                            <p className="join-date">Joined {new Date(user.created_at).toLocaleDateString()}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Community;
