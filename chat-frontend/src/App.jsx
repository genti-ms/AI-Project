import React, { useState, useRef, useEffect } from "react";
import profilePic from "./assets/chatbot.png";
import "./app.css";

export default function App() {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hallo! Wie kann ich dir helfen?", sender: "bot" },
  ]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  const sendMessage = () => {
    if (!input.trim()) return;
    setMessages((prev) => [
      ...prev,
      { id: Date.now(), text: input, sender: "user" },
      {
        id: Date.now() + 1,
        text: "Danke für deine Nachricht!",
        sender: "bot",
      },
    ]);
    setInput("");
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <div className="app">
      <header className="chat-header">
        <img src={profilePic} alt="Profil" className="profile-pic" />
        <h1 className="chat-title">Chatbot</h1>
      </header>

      <div className="chat-container">
        <div className="messages">
          {messages.map(({ id, text, sender }) => (
            <div key={id} className={`message ${sender}`}>
              {text}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <input
            type="text"
            placeholder="Nachricht schreiben..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button onClick={sendMessage}>Senden</button>
        </div>
      </div>
    </div>
  );
}
