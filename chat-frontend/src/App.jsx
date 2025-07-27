import React, { useState, useRef, useEffect } from 'react';
import './App.css';

import salesImg from './assets/sales.jpg';
import employeesImg from './assets/employees.webp';
import supportImg from './assets/Customer-Support-Team.jpg';

const chats = [
  { id: 'Sales', name: 'Sales - Management', image: salesImg },
  { id: 'Employee', name: 'Employees - Service', image: employeesImg },
  { id: 'Customer', name: 'Customer - Service', image: supportImg },
];

export default function App() {
  const [activeChat, setActiveChat] = useState(chats[0].id);
  const [input, setInput] = useState('');
  const [error, setError] = useState(null);
  const chatRef = useRef(null);

  // Nachrichten pro Chat speichern
  const [chatMessages, setChatMessages] = useState(() => {
    const saved = localStorage.getItem('chatMessages');
    return saved ? JSON.parse(saved) : {
      swati: [{ sender: 'bot', text: 'Hallo! Wie kann ich dir helfen?' }],
      chintu: [],
      pinder: [],
    };
  });

  // Scroll nach unten & speichern
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
    localStorage.setItem('chatMessages', JSON.stringify(chatMessages));
  }, [chatMessages, activeChat]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input };
    const updated = {
      ...chatMessages,
      [activeChat]: [...(chatMessages[activeChat] || []), userMessage],
    };
    setChatMessages(updated);
    setInput('');
    setError(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        throw new Error(`Server antwortet mit Status ${response.status}`);
      }

      const data = await response.json();
      const botMessage = { sender: 'bot', text: data.response };

      setChatMessages((prev) => ({
        ...prev,
        [activeChat]: [...prev[activeChat], botMessage],
      }));
    } catch (err) {
      setError(err.message);
      setChatMessages((prev) => ({
        ...prev,
        [activeChat]: [...prev[activeChat], { sender: 'bot', text: 'Fehler bei der Antwort.' }],
      }));
    }
  };

  const handleChatClick = (id) => {
    setActiveChat(id);
  };

  const currentMessages = chatMessages[activeChat] || [];

  return (
    <div className="container">
      <div className="sidebar">
        <h3>Chats</h3>
        {chats.map((chat) => (
          <div
            key={chat.id}
            className={`chat-tab ${activeChat === chat.id ? 'active' : ''}`}
            onClick={() => handleChatClick(chat.id)}
          >
            <img src={chat.image} alt={chat.name} className="avatar" />
            <span>{chat.name}</span>
          </div>
        ))}
      </div>

      <div className="chat-area">
        <div className="chat-header">
            <img
             src={chats.find((c) => c.id === activeChat)?.image}
             alt="Profil"
             className="avatar header-avatar"
            />
            <span>{chats.find((c) => c.id === activeChat)?.name}</span>
        </div>


        <div id="chat" ref={chatRef}>
          {currentMessages.map((msg, i) => (
            <div
              key={i}
              className={`message ${msg.sender}`}
              {...(msg.sender === 'bot' ? { dangerouslySetInnerHTML: { __html: msg.text } } : {})}
            >
              {msg.sender === 'user' ? msg.text : null}
            </div>
          ))}
        </div>

        {error && <div className="error-message">⚠️ {error}</div>}

        <form id="inputForm" onSubmit={sendMessage}>
          <input
            id="messageInput"
            autoComplete="off"
            placeholder="Nachricht eingeben..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" id="sendBtn">Senden</button>
        </form>
      </div>
    </div>
  );
}
