import React, { useState, useRef, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import axios from "axios";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";
import "./App.css";

import logo from "./assets/Dattabuddy.png";
import salesAvatar from "./assets/sales.jpg";
import productAvatar from "./assets/Customer-Support-Team.jpg";
import teamAvatar from "./assets/employees.webp";

function App() {
  const [chats, setChats] = useState([
    {
      id: "1",
      name: "Sales - Datenbuddy",
      avatar: salesAvatar,
      messages: [
        { id: uuidv4(), sender: "bot", text: "Hallo 👋, was möchtest du zu unseren Sales wissen?", time: new Date() },
      ],
    },
    {
      id: "2",
      name: "Produkt - Datenbuddy",
      avatar: productAvatar,
      messages: [
        { id: uuidv4(), sender: "bot", text: "Willkommen bei der Produkt-Information 💬", time: new Date() },
      ],
    },
    {
      id: "3",
      name: "Team - Datenbuddy",
      avatar: teamAvatar,
      messages: [
        { id: uuidv4(), sender: "bot", text: "Team-Chat geöffnet 🚀", time: new Date() },
      ],
    },
    {
      id: "4",
      name: "Customer - Datenbuddy",
      avatar: productAvatar,
      messages: [
        { id: uuidv4(), sender: "bot", text: "Willkommen beim Customer-Support 💬", time: new Date() },
      ],
    },
  ]);

  const [activeChatId, setActiveChatId] = useState("1");
  const [input, setInput] = useState("");
  const [awaitingFollowUp, setAwaitingFollowUp] = useState(false);
  const messagesEndRef = useRef(null);
  const activeChat = chats.find((c) => c.id === activeChatId);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeChat?.messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: uuidv4(),
      sender: "user",
      text: input,
      time: new Date(),
    };

    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === activeChatId
          ? { ...chat, messages: [...chat.messages, userMessage] }
          : chat
      )
    );

    const userInputLower = input.toLowerCase();
    setInput("");

    // Follow-Up Logik
    if (awaitingFollowUp) {
      handleFollowUp(userInputLower);
      return;
    }

    try {
      const response = await axios.post("http://localhost:8000/ask", {
        query: input,
      });

      const resultsHtml = response.data.results_html || "";
      const sqlQuery = response.data.query || "";
      const parsedTable = resultsHtml ? parseHTMLTable(resultsHtml) : null;

      let botText = "Hier sind die Ergebnisse:";

      // Prüfen, ob Nutzer „alle“/„all“ geschrieben hat
      const isAllQuery = /alle|all/i.test(userInputLower);

      let sentence = "";
      if (parsedTable && !isAllQuery) {
        sentence = generateSentence(parsedTable, activeChat.name);
      }

      const botMessage = {
        id: uuidv4(),
        sender: "bot",
        text: sentence ? botText + "\n" + sentence : botText,
        time: new Date(),
        table: parsedTable,
        query: sqlQuery,
      };

      setChats(prevChats =>
        prevChats.map(chat =>
          chat.id === activeChatId
            ? { ...chat, messages: [...chat.messages, botMessage] }
            : chat
        )
      );

      // Follow-Up Nachricht
      const followUpMessage = {
        id: uuidv4(),
        sender: "bot",
        text: "Kann ich dir sonst mit Daten helfen? Benötigst du noch Infos (Ja/Nein?)",
        time: new Date(),
      };
      setChats(prevChats =>
        prevChats.map(chat =>
          chat.id === activeChatId
            ? { ...chat, messages: [...chat.messages, followUpMessage] }
            : chat
        )
      );
      setAwaitingFollowUp(true);

    } catch (err) {
      const errorMessage = {
        id: uuidv4(),
        sender: "bot",
        text: err.response?.data?.detail || "❌ Fehler beim Abrufen der Daten.",
        time: new Date(),
      };
      setChats(prevChats =>
        prevChats.map(chat =>
          chat.id === activeChatId
            ? { ...chat, messages: [...chat.messages, errorMessage] }
            : chat
        )
      );
      console.error(err);
    }
  };

  const handleFollowUp = (inputLower) => {
    let responseText = "";
    if (/\bja\b/i.test(inputLower)) {
      responseText = "Super! 😊 Bitte gib mir genau an, welche Daten du benötigst.";
      setAwaitingFollowUp(false);
    } else if (/\bnein\b/i.test(inputLower)) {
      responseText = "Alles klar! Ich wünsche dir einen schönen Tag! 👋";
      setAwaitingFollowUp(false);
    } else {
      responseText = "Ich konnte deine Eingabe nicht verstehen. Bitte antworte nur mit 'Ja' oder 'Nein'.";
    }

    const followMessage = {
      id: uuidv4(),
      sender: "bot",
      text: responseText,
      time: new Date(),
    };

    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === activeChatId
          ? { ...chat, messages: [...chat.messages, followMessage] }
          : chat
      )
    );
  };

  const parseHTMLTable = (html) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");
    const rows = Array.from(doc.querySelectorAll("tr"));
    return rows.map(tr =>
      Array.from(tr.children).map(td => td.textContent.trim())
    );
  };

  const generateSentence = (table, chatType) => {
    if (!table || table.length < 2) return "";

    const headers = table[0];
    const row = table[1];
    const data = {};
    headers.forEach((h, i) => (data[h] = row[i]));

    switch (chatType.toLowerCase()) {
      case "sales - datenbuddy":
        return `💰 Der letzte Verkauf:\nKunde: **ID ${data.customer_id}** 🧑‍🤝‍🧑\nProdukt: **ID ${data.product_id}** 🛒\nMenge: **${data.quantity}**, Gesamtbetrag: **${data.total_amount}€** 💵\nDatum: **${data.sale_date}**, Stadt: **${data.city}** 🏙️`;
      case "produkt - datenbuddy":
        return `📦 Produktinfo:\nName: **${data.name}** (ID ${data.id})\nPreis: **${data.price}€** 💵\nBeschreibung: ${data.description}\nVerfügbar: **${data.stock} Stück**`;
      case "team - datenbuddy":
        return `👤 Mitarbeiter:\nName: **${data.first_name} ${data.last_name}**\nPosition: **${data.position}** 💼\nE-Mail: ✉️ ${data.email}`;
      case "customer - datenbuddy":
        return `🧑‍🤝‍🧑 Kunde:\nName: **${data.name}** (ID ${data.id})\nE-Mail: ✉️ ${data.email}\nStadt: **${data.city}**, Land: **${data.country}**`;
      default:
        return "";
    }
  };

  const renderMessage = (msg) => {
    if (msg.table && msg.table.length > 0) {
      return (
        <>
          <span style={{ whiteSpace: "pre-line" }}>{msg.text}</span>
          <TableContainer component={Paper} className="table-container" style={{ marginTop: "8px" }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {msg.table[0].map((col, idx) => (
                    <TableCell key={idx}>{col}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {msg.table.slice(1).map((row, idx) => (
                  <TableRow key={idx}>
                    {row.map((cell, i) => (
                      <TableCell key={i}>{cell}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          {msg.query && (
            <div className="sql-query" style={{ marginTop: "4px", fontStyle: "italic", fontSize: "0.9em" }}>
              SQL: {msg.query}
            </div>
          )}
        </>
      );
    }

    return <span style={{ whiteSpace: "pre-line" }}>{msg.text}</span>;
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="logo-container">
            <img src={logo} alt="Data Buddy" className="logo" />
            <span className="app-name">Data Buddy</span>
          </div>
        </div>
        <div className="chat-list">
          {chats.map(chat => (
            <div
              key={chat.id}
              className={`chat-item ${chat.id === activeChatId ? "active" : ""}`}
              onClick={() => setActiveChatId(chat.id)}
            >
              <img src={chat.avatar} alt={chat.name} />
              <div className="chat-info">
                <div className="chat-info-top">
                  <span className="chat-name">{chat.name}</span>
                  <span className="chat-time">
                    {chat.messages.length > 0 &&
                      new Date(chat.messages[chat.messages.length - 1].time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  </span>
                </div>
                <div className="chat-last">
                  {chat.messages.length > 0 ? chat.messages[chat.messages.length - 1].text.slice(0, 30) + (chat.messages[chat.messages.length - 1].text.length > 30 ? "..." : "") : "Keine Nachrichten"}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="chat-area">
        <div className="chat-header">
          <img src={activeChat.avatar} alt={activeChat.name} />
          <span>{activeChat.name}</span>
        </div>

        <div className="messages">
          {activeChat.messages.map(msg => (
            <div key={msg.id} className={`message ${msg.sender}`}>
              {renderMessage(msg)}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Nachricht schreiben..."
          />
          <button onClick={sendMessage}>Senden</button>
        </div>
      </div>
    </div>
  );
}

export default App;
