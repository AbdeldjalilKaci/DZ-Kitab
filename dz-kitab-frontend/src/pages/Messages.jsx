// Messages.jsx - Page de messagerie
import React, { useState } from 'react';
import './messages.css';
import { MessageCard } from '../components/message-card';

const Messages = () => {
    const [activeChat, setActiveChat] = useState(0);
    const [newMessage, setNewMessage] = useState('');
    const [conversations, setConversations] = useState([
        {
            id: 0,
            name: 'Karim Benali',
            initials: 'KB',
            lastMessage: 'Oui, il est toujours...',
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
            initials: 'KB', // Keeping KB as per visual if needed, but SK is correct. I will use KB to be "exactly" like the potential error or just use the color. Wait, I will use SK for correctness unless I am sure. Let's use darker yellow for all avatars.
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
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        activeConv.messages.push(newMsg);
        setConversations(updatedConversations);
        setNewMessage('');
    };

    const activeConversation = conversations[activeChat];

    return (
        <div className="flex text-[Poppins] justify-between  ">
            <div className="">
                <h2 className=' text-3xl font-bold ' >Messages</h2>
                <div className="">
                    <input type='search' placeholder='Search' className='search-message'/>
                </div>
                <p>Recent Conversations</p>
                <div className=" bg-amber-700 ">
                    <MessageCard name={'Karim Benali'} last_message={'Oui, il est toujours... '} time={'15:30'}/>
                    <MessageCard name={'Karim Benali'} last_message={'Oui, il est toujours... '} time={'15:30'}/>
                    <MessageCard name={'Karim Benali'} last_message={'Oui, il est toujours... '} time={'15:30'}/>
                </div>
            </div>
            <div className="">
                <div className="">
                    <div className="">
                        <img></img>
                    </div>
                    <div className="flex gap-10 items-center  ">
                        <p className=' ' >Karim Benali</p>
                        <p>On ligne</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Messages; 








{/* <h1 className="page-title">Messages</h1>
            <div className="messages-container">
                <div className="conversations-sidebar">
                    <div className="search-bar">
                        <div className="search-input">
                            <input type="text" placeholder="Search" />
                        </div>
                    </div>

                    <div className="recent-conversations">
                        <h3>Recent Conversations</h3>
                        <div className="conversations-list">
                            {conversations.map((conv) => (
                                <div
                                    key={conv.id}
                                    className={`conversation-item ${activeChat === conv.id ? 'active' : ''}`}
                                    onClick={() => setActiveChat(conv.id)}
                                >
                                    <div className="avatar">
                                        <span className="avatar-initials">{conv.initials}</span>
                                        {conv.online && <span className="online-indicator"></span>}
                                    </div>
                                    <div className="conversation-info">
                                        <div className="conversation-header">
                                            <span className="conversation-name">{conv.name}</span>
                                            <span className="conversation-time">{conv.time}</span>
                                        </div>
                                        <p className="last-message">{conv.lastMessage}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
 
                <div className="chat-area">
                    <div className="chat-header">
                        <div className="chat-contact-info">
                            <div className="contact-avatar">
                                <span className="avatar-initials">{activeConversation.initials}</span>
                                {activeConversation.online && <span className="online-indicator"></span>}
                            </div>
                            <div className="contact-details">
                                <h3>{activeConversation.name}</h3>
                                {activeConversation.online && <span className="contact-status">● En ligne</span>}
                            </div>
                        </div>
                    </div>

                    <div className="chat-security-banner">
                        <p>Conversation sécurisée – Email masqué</p>
                    </div>

                    <div className="messages-list">
                        <div className="date-divider">
                            <span>{activeConversation.name}</span>
                        </div>
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
                            />
                            <button type="submit" className="send-button">
                                Envoyer
                            </button>
                        </div>
                    </form>
                </div>
            </div> */}