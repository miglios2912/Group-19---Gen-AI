import { useState, useEffect } from "react";

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // Show welcome message on first load
  useEffect(() => {
    setMessages([
      { role: "bot", text: "👋 Welcome to the TUM Onboarding Assistant!" }
    ]);
  }, []);

  const sendMessage = () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    const botMessage = { role: "bot", text: "Thinking..." };

    setMessages([...messages, userMessage, botMessage]);
    setInput("");

    setTimeout(() => {
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { role: "bot", text: `Response to: "${input}"` },
      ]);
    }, 800);
  };

  return (
    <div className="flex flex-col h-full p-6 bg-white rounded-xl">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`px-4 py-2 rounded-2xl max-w-[75%] whitespace-pre-wrap shadow-sm ${
              msg.role === "user"
                ? "bg-tumblue text-white self-end"
                : "bg-lightgray text-anthracite self-start"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>

      {/* Input area */}
      <div className="pt-4">
        <div className="flex shadow-md rounded-xl overflow-hidden border border-gray-300">
          <input
            className="flex-1 p-3 text-sm outline-none bg-white"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask me anything about onboarding at TUM..."
          />
          <button
            className="bg-tumblue text-white px-6 text-sm hover:bg-tumhover transition"
            onClick={sendMessage}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
