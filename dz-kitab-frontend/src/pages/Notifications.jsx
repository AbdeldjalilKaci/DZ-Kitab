import React, { useState, useEffect } from 'react';
import api from '../utils/api';
// import './Notifications.css'; // We'll create a basic CSS or use inline styles

const Notifications = () => {
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                // Fetch notifications (mock: query unread or all, here fetch all)
                const res = await api.get('/api/notifications');
                // The backend returns { notifications: [...] }
                setNotifications(res.data.notifications || []);
            } catch (error) {
                console.error("Error fetching notifications:", error);
            } finally {
                setLoading(false);
            }
        }
        fetchNotifications();
    }, []);

    return (
        <div className="notifications-page">
            <div className="container mx-auto px-4 py-8 min-h-[60vh]">
                <h1 className="text-2xl font-bold mb-6">Notifications</h1>
                {loading ? (
                    <p>Loading...</p>
                ) : (
                    <div className="space-y-4">
                        {notifications.length === 0 ? (
                            <p className="text-gray-500">No new notifications.</p>
                        ) : (
                            notifications.map(notif => (
                                <div key={notif.id} className={`p-4 rounded-lg border ${notif.read ? 'bg-gray-50' : 'bg-white border-blue-200 shadow-sm'}`}>
                                    <h3 className="font-semibold">{notif.title}</h3>
                                    <p className="text-gray-600">{notif.message}</p>
                                    <span className="text-xs text-gray-400">{new Date(notif.date).toLocaleDateString()}</span>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Notifications;
