import { useState, useEffect, useRef } from "react";
import "./ChatWindow.css"; // Make sure this file exists and is linked

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [copiedIndex, setCopiedIndex] = useState(null); // State to track which message is copied
  const fileInputRef = useRef(null);

  useEffect(() => {
    setMessages([
      { role: "bot", text: "👋 Welcome to the TUM Onboarding Assistant!" },
      {
        role: "bot",
        text: "Hello I am the Tum Chat-bot On boarding Assistant. I can help you get right on track, with your research aspirations in TUM. What is your role in the University and what step of the process are you in. Specifically do you require assistance with X,Y,Z",
      },
    ]);
  }, []);

  const sendMessage = () => {
    if (!input.trim()) return;
    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    
    setTimeout(() => {
        setMessages((prev) => [...prev, { role: 'bot', text: `🧠 Here's a response to: "${userMessage.text}"` }]);
    }, 800);
  };

  const handleCopy = (text, index) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000); // Reset after 2 seconds
    });
  };

  const handleAttachClick = () => fileInputRef.current.click();

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const fileMessage = { role: 'user', text: `📎 Attached: ${file.name}` };
      setMessages((prev) => [...prev, fileMessage]);
      event.target.value = null;
    }
  };

  return (
    <div className="chat-window">
      {/* Header is now inside the chat window */}
      <header className="chat-header-internal">
        <img src="/tum-logo.png" alt="TUM Logo" className="chat-logo-internal" />
      </header>

      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message-container ${msg.role}`}>
            <div className={`message ${msg.role}`}>
              {msg.text}
            </div>
            {msg.role === 'bot' && (
              <button onClick={() => handleCopy(msg.text, i)} className="copy-button">
                {copiedIndex === i ? 'Copied!' : 'Copy'}
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="input-bar">
        <button className="attach-button" onClick={handleAttachClick}>+</button>
        <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileChange} accept="application/pdf,image/jpeg,image/png" />
        <input className="input-field" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && sendMessage()} placeholder="Ask me anything..." />
        <button className="send-button" onClick={sendMessage}>Send</button>
      </div>
      
      <div className="action-links">
        <a href="mailto:onboarding-support@tum.de" className="action-link">Ask for Help</a>
        <a href="https://your-suggestion-form-url.com" target="_blank" rel="noopener noreferrer" className="action-link">Suggest Improvement</a>
      </div>
    </div>
  );
}