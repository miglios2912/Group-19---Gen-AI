import { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";

// Simple markdown parser for basic formatting
const parseMarkdown = (text) => {
  if (!text) return text;
  
  // Convert markdown to HTML
  let html = text
    // Bold: ****text**** or **text**
    .replace(/\*{4}([^*]+)\*{4}/g, '<strong>$1</strong>')
    .replace(/\*{2}([^*]+)\*{2}/g, '<strong>$1</strong>')
    // Italic: *text*
    .replace(/\*([^*]+)\*/g, '<em>$1</em>')
    // Links: [text](url)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    // Email links: email@domain.com
    .replace(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g, '<a href="mailto:$1">$1</a>')
    // Line breaks
    .replace(/\n/g, '<br/>');
    
  return html;
};

// Backend API configuration
// In Cloud Run, the frontend and backend are served from the same origin
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (window.location.hostname === 'localhost' ? "http://localhost:8083" : "");

console.log("API_BASE_URL:", API_BASE_URL);
console.log("VITE_API_BASE_URL:", import.meta.env.VITE_API_BASE_URL);

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [userId] = useState(`user_${Math.random().toString(36).substr(2, 9)}`);
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [hasUserMessage, setHasUserMessage] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize session on component mount
  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v2/session/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-ID": userId,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);

        // Set initial welcome messages - empty for mobile
        setMessages([]);
      } else {
        console.error("Failed to initialize session");
        setMessages([]);
      }
    } catch (error) {
      console.error("Error initializing session:", error);
      setMessages([]);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    
    // Set hasUserMessage to true after first user message
    if (!hasUserMessage) {
      setHasUserMessage(true);
    }

    // Blur input to hide mobile keyboard
    inputRef.current?.blur();

    try {
      const response = await fetch(`${API_BASE_URL}/api/v2/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-ID": userId,
          "X-Session-ID": sessionId || "default",
        },
        body: JSON.stringify({
          message: userMessage.text,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessages((prev) => [
          ...prev,
          {
            role: "bot",
            text: data.response,
          },
        ]);
      } else {
        const errorData = await response.json();
        setMessages((prev) => [
          ...prev,
          {
            role: "bot",
            text: `I apologize, but I encountered an error: ${
              errorData.error || "Unknown error"
            }. Please try again or contact support if the problem persists.`,
          },
        ]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      console.error("Error details:", error.message);
      console.error("Full error:", JSON.stringify(error, Object.getOwnPropertyNames(error)));
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: `Connection error: ${error.message}. API URL: ${API_BASE_URL}/api/v2/chat`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async (text, index) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (error) {
      console.error("Failed to copy text:", error);
    }
  };


  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey && !isLoading) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Sample questions for rotating placeholder
  const sampleQuestions = [
    "How do I set up my TUM email?",
    "Where can I eat on campus?",
    "What is eduroam setup?",
    "Where is the library?",
    "How do I register for courses?",
    "Where can I print documents?",
    "How do I get my student ID card?"
  ];

  // Rotate placeholder text every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % sampleQuestions.length);
    }, 3000);

    return () => clearInterval(interval);
  }, [sampleQuestions.length]);

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };


  // Cleanup session on component unmount
  useEffect(() => {
    return () => {
      if (sessionId) {
        fetch(`${API_BASE_URL}/api/v2/session/${sessionId}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            "X-User-ID": userId,
          },
        }).catch((error) => {
          console.error("Error ending session:", error);
        });
      }
    };
  }, [sessionId, userId]);

  return (
    <div className="chat-window">
      <div className="chat-header-mobile">
        <img src="/tum-logo.png" alt="TUM Logo" className="chat-logo-mobile" />
        <div className="chat-status">
          <span className="status-indicator"></span>
          <span className="status-text">Online</span>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-animation-mobile">
            <div className="welcome-content">
              <div className="typing-text" data-text="Welcome to TUM Onboarding Assistant">
                <span></span>
              </div>
              <div className="subtitle-text">
                I can help you with campus navigation, course registration, IT setup, and more
              </div>
              <div className="campus-info">
                👋 Tell me your role and which campus you're at to get started
              </div>
            </div>
          </div>
        )}
        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`message-wrapper ${msg.role}`}>
              <div className={`message-bubble ${msg.role}`}>
                <div 
                  className="message-content"
                  dangerouslySetInnerHTML={{ __html: parseMarkdown(msg.text) }}
                />
                {msg.role === "bot" && (
                  <button
                    onClick={() => handleCopy(msg.text, i)}
                    className="copy-button-mobile"
                    title="Copy to clipboard"
                  >
                    {copiedIndex === i ? (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="20,6 9,17 4,12"/>
                      </svg>
                    ) : (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                      </svg>
                    )}
                  </button>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message-wrapper bot">
              <div className="message-bubble bot loading">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>


      <div className="input-container floating">
        <div className="input-bar-mobile">
          <div className="input-wrapper">
            <textarea
              ref={inputRef}
              className="input-field-mobile"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={sampleQuestions[placeholderIndex]}
              disabled={isLoading}
              rows={1}
            />
          </div>
          <button
            className="send-button-mobile"
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            title="Send message"
          >
            {isLoading ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="send-button-spinner">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M7.33 24l-2.83-2.829 9.339-9.175-9.339-9.167 2.83-2.829 12.17 11.996z"/>
              </svg>
            )}
          </button>
        </div>

      </div>

    </div>
  );
}
