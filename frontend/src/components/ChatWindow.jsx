import { useState, useEffect } from "react";
import "./ChatWindow.css"; // Make sure this file exists and is linked

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    setMessages([
      { role: "bot", text: "👋 Welcome to the TUM Onboarding Assistant!" },
    ]);
  }, []);

  const sendMessage = () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    const botMessage = { role: "bot", text: "Processing your question..." };

    setMessages((prev) => [...prev, userMessage, botMessage]);
    setInput("");

    setTimeout(() => {
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { role: "bot", text: `🧠 Here's a response to: "${input}"` },
      ]);
    }, 800);
  };

  return (
    <div className="chat-window">
      <div className="messages">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`message ${msg.role === "user" ? "user" : "bot"}`}
          >
            {msg.text}
          </div>
        ))}
      </div>

      <div className="input-bar">
        <input
          className="input-field"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask me anything about onboarding at TUM..."
        />
        <button className="send-button" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}
