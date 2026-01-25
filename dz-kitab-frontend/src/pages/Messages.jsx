import React, { useState, useEffect } from 'react';
import './messages.css';
import { CiSearch } from "react-icons/ci";
import api from "../utils/api";
const Messages = () => {
    const [activeChat, setActiveChat] = useState(null); // Use conversation ID or Object
    const [newMessage, setNewMessage] = useState('');
    const [conversations, setConversations] = useState([]);
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(true);

    // Fetch conversations on load
    useEffect(() => {
        const fetchConversations = async () => {
            try {
                const res = await api.get('/api/messages/conversations');
                setConversations(res.data.conversations);
                if (res.data.conversations.length > 0) {
                    setActiveChat(res.data.conversations[0]); // Select first chat by default
                }
            } catch (error) {
                console.error("Error fetching conversations:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchConversations();
    }, []);

    // Fetch messages when activeChat changes
    useEffect(() => {
        if (activeChat) {
            const fetchMessages = async () => {
                try {
                    const res = await api.get(`/api/messages/conversations/${activeChat.id}`);
                    setMessages(res.data.messages);
                } catch (error) {
                    console.error("Error fetching messages:", error);
                }
            };
            fetchMessages();
        }
    }, [activeChat]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!newMessage.trim() || !activeChat) return;

        try {
            const res = await api.post(`/api/messages/conversations/${activeChat.id}/messages`, null, {
                params: { content: newMessage }
            });
            // Add new message to UI immediately
            setMessages([...messages, res.data]);
            setNewMessage('');
        } catch (error) {
            console.error("Error sending message:", error);
            alert("Failed to send message");
        }
    };

    return (
        <div className="messages-page">
            <div className="messages-container">
                <div className="conversations-sidebar">
                    <h2 className="messages-title">Messages</h2>
                    <div className="search-bar flex gap-2 ">
                        <CiSearch />
                        <input type="text" placeholder="Search" className=" h-full  outline-none border-0 focus:outline-none focus:border-0 " />
                    </div>
                    <div className="recent-conversations">
                        <h3 className="recent-title">Recent Conversations</h3>
                        <div className="conversations-list">
                            {loading ? <p>Loading chats...</p> : conversations.map((conv) => (
                                <div
                                    key={conv.id}
                                    className={`conversation-item ${activeChat?.id === conv.id ? 'active' : ''}`}
                                    onClick={() => setActiveChat(conv)}
                                >
                                    <div className="avatar">
                                        <span className="avatar-initials">{conv.other_user_username.substring(0, 2).toUpperCase()}</span>
                                    </div>
                                    <div className="conversation-info">
                                        <div className="conversation-header">
                                            <span className="conversation-name">{conv.other_user_username}</span>
                                            <span className="conversation-time">{new Date(conv.last_message_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                        </div>
                                        <p className="last-message loading-dots ">{conv.last_message}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="chat-area relative rounded-tl-[10px] ">
                    <div className="absolute left-0 top-0 h-full w-1 rounded-tr-[10px]  bg-linear-to-b from-[#e3e3fd]  to-[#e2dad8]"></div>
                    {activeChat ? (
                        <>
                            <div className="chat-header">
                                <div className="chat-contact-info">
                                    <div className="contact-avatar">
                                        <span className="avatar-initials">{activeChat.other_user_username.substring(0, 2).toUpperCase()}</span>
                                    </div>
                                    <div className="contact-details">
                                        <h3>{activeChat.other_user_username}</h3>
                                        {activeChat.announcement_title && (
                                            <span className="text-sm text-gray-500">
                                                Ref: {activeChat.announcement_title}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <div className="chat-security-banner">
                                <p>Conversation sécurisée - Email masqué</p>
                            </div>

                            <div className="messages-list">
                                {messages.map((msg) => (
                                    <div
                                        key={msg.id}
                                        className={`message ${msg.sender_id !== activeChat.other_user_id ? 'sent' : 'received'}`}
                                    >
                                        <div className="message-content">
                                            <p>{msg.content}</p>
                                        </div>
                                        <span className="message-time">{new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                    </div>
                                ))}
                            </div>

                            <form className="message-input-form" onSubmit={handleSendMessage}>
                                <div className="input-wrapper">
                                    <input
                                        type="text"
                                        placeholder="Taper pour ecrire..."
                                        value={newMessage}
                                        onChange={(e) => setNewMessage(e.target.value)}
                                        className="message-input"
                                    />
                                    <button type="submit" className="send-button">
                                        Envoyer
                                    </button>
                                </div>
                            </form>
                        </>
                    ) : (
                        <div className="flex items-center justify-center h-full text-gray-500">
                            Select a conversation to start messaging
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Messages;
