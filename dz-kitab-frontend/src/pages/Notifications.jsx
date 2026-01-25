import React, { useState, useEffect } from 'react';
import api from '../utils/api';
// import './Notifications.css'; // We'll create a basic CSS or use inline styles

import { useNavigate } from 'react-router-dom';

const Notifications = () => {
    const navigate = useNavigate();
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchNotifications = async () => {
        try {
            const res = await api.get('/api/notifications');
            console.log("Notifications received:", res.data.notifications);
            setNotifications(res.data.notifications || []);
        } catch (error) {
            console.error("Error fetching notifications:", error);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchNotifications();
        const interval = setInterval(fetchNotifications, 10000); // Poll every 10s
        return () => clearInterval(interval);
    }, []);

    const handleNotificationClick = async (notif) => {
        // Mark as read in backend
        if (!notif.is_read) {
            try {
                await api.put(`/api/notifications/${notif.id}/read`);
                // Update local state
                setNotifications(notifications.map(n =>
                    n.id === notif.id ? { ...n, is_read: true } : n
                ));
            } catch (error) {
                console.error("Error marking notification as read:", error);
            }
        }

        // Navigate if action_url exists
        if (notif.action_url) {
            navigate(notif.action_url);
        }
    };

    const markAllRead = async () => {
        try {
            await api.put('/api/notifications/read-all');
            setNotifications(notifications.map(n => ({ ...n, is_read: true })));
        } catch (error) {
            console.error("Error marking all as read:", error);
        }
    };

    return (
        <div className="notifications-page">
            <div className="container mx-auto px-4 py-8 min-h-[60vh]">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold">Notifications</h1>
                    {notifications.some(n => !n.is_read) && (
                        <button
                            onClick={markAllRead}
                            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                        >
                            Mark all as read
                        </button>
                    )}
                </div>

                {loading ? (
                    <p>Loading...</p>
                ) : (
                    <div className="flex flex-col gap-4">
                        {notifications.length === 0 ? (
                            <p className="text-gray-500 text-center py-10">No notifications yet.</p>
                        ) : (
                            notifications.map(notif => (
                                <div
                                    key={notif.id}
                                    onClick={() => handleNotificationClick(notif)}
                                    className={`p-4 rounded-lg border cursor-pointer transition-all hover:shadow-md ${notif.is_read ? 'bg-gray-50 border-gray-200' : 'bg-white border-blue-200 shadow-sm'
                                        }`}
                                >
                                    <div className="flex justify-between items-start">
                                        <h3 className={`font-semibold ${notif.is_read ? 'text-gray-700' : 'text-blue-900'}`}>
                                            {notif.title}
                                        </h3>
                                        {!notif.is_read && <span className="h-2 w-2 bg-blue-600 rounded-full"></span>}
                                    </div>
                                    <p className="text-gray-600 mt-1">{notif.message}</p>
                                    <div className="mt-2 text-xs text-gray-400">
                                        {new Date(notif.created_at).toLocaleString()}
                                    </div>
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
