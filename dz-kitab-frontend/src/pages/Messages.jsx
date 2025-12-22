import React, { useState } from 'react';
import './messages.css';
import { CiSearch } from "react-icons/ci";
const Messages = () => {
    const [activeChat, setActiveChat] = useState(0);
    const [newMessage, setNewMessage] = useState('');
    const [conversations, setConversations] = useState([
        {
            id: 0,
            name: 'Karim Benali',
            initials: 'KB',
            lastMessage: 'Oui, il est toujours lfohawifhrihgiehirusenfse ruivhsidhinvsien',
            time: '15:10',
            online: true,
            messages: [
                { id: 1, text: 'Bonjour, le livre Artificial Intelligence est-il toujours disponible ?', sender: 'them', time: '15:06' },
                { id: 2, text: 'Oui, il est toujours disponible. Il est en excellent état !', sender: 'me', time: '15:10' }
            ]
        },
        {
            id: 1,
            name: 'Sarah Mourad',
            initials: 'SM',
            lastMessage: 'Bonjour, il y a...',
            time: '22:43',
            online: false,
            messages: [
                { id: 1, text: 'Bonjour, je voulais savoir si le livre est disponible en format numérique ?', sender: 'them', time: '22:43' },
            ]
        },
        {
            id: 2,
            name: 'Sami Kamel',
            initials: 'SK',
            lastMessage: 'Désolé je peut pas...',
            time: '09:30',
            online: true,
            messages: [
                { id: 1, text: 'Désolé je peut pas vous le vendre pour le moment.', sender: 'them', time: '09:30' }
            ]
        }
    ]);

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (!newMessage.trim()) return;

        const updatedConversations = [...conversations];
        const activeConv = updatedConversations[activeChat];

        const newMsg = {
            id: activeConv.messages.length + 1,
            text: newMessage,
            sender: 'me',
            time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
        };

        activeConv.messages.push(newMsg);
        setConversations(updatedConversations);
        setNewMessage('');
    };

    const activeConversation = conversations[activeChat];

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
                            {conversations.map((conv) => (
                                <div
                                    key={conv.id}
                                    className={`conversation-item ${activeChat === conv.id ? 'active' : ''}`}
                                    onClick={() => setActiveChat(conv.id)}
                                >
                                    <div className="avatar">
                                        <span className="avatar-initials">{conv.initials}</span>
                                    </div>
                                    <div className="conversation-info">
                                        <div className="conversation-header">
                                            <span className="conversation-name">{conv.name}</span>
                                            <span className="conversation-time">{conv.time}</span>
                                        </div>
                                        <p className="last-message loading-dots ">{conv.lastMessage}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="chat-area relative rounded-tl-[10px] ">
                <div className="absolute left-0 top-0 h-full w-1 rounded-tr-[10px]  bg-linear-to-b from-[#e3e3fd]  to-[#e2dad8]"></div>
                    <div className="chat-header">
                        <div className="chat-contact-info">
                            <div className="contact-avatar">
                                <span className="avatar-initials">{activeConversation.initials}</span>
                            </div>
                            <div className="contact-details">
                                <h3>{activeConversation.name}</h3>
                                {activeConversation.online && (
                                    <span className="contact-status">
                                        <span className="online-dot"></span> En ligne
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="chat-security-banner">
                        <p>Conversation sécurisée - Email masqué</p>
                    </div>

                    <div className="messages-list">
                        {activeConversation.messages.map((msg) => (
                            <div
                                key={msg.id}
                                className={`message ${msg.sender === 'me' ? 'sent' : 'received'}`}
                            >
                                <div className="message-content">
                                    <p>{msg.text}</p>
                                </div>
                                <span className="message-time">{msg.time}</span>
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
                </div>
            </div>
        </div>
    );
};

export default Messages;
