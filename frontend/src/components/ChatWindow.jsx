import { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";

// Backend API configuration
const API_BASE_URL =
	import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

export default function ChatWindow() {
	const [messages, setMessages] = useState([]);
	const [input, setInput] = useState("");
	const [copiedIndex, setCopiedIndex] = useState(null);
	const [isLoading, setIsLoading] = useState(false);
	const [sessionId, setSessionId] = useState(null);
	const [userId] = useState(`user_${Math.random().toString(36).substr(2, 9)}`);
	const fileInputRef = useRef(null);

	// Initialize session on component mount
	useEffect(() => {
		initializeSession();
	}, []);

	const initializeSession = async () => {
		try {
			const response = await fetch(`${API_BASE_URL}/api/session/start`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-User-ID": userId,
				},
			});

			if (response.ok) {
				const data = await response.json();
				setSessionId(data.session_id);

				// Set initial welcome messages
				setMessages([
					{ role: "bot", text: "Welcome to the TUM Onboarding Assistant!" },
					{
						role: "bot",
						text: "Hello! I am the TUM Chat-bot Onboarding Assistant. I can help you get right on track with your research aspirations at TUM. What is your role in the University and what step of the process are you in?",
					},
				]);
			} else {
				console.error("Failed to initialize session");
				setMessages([
					{ role: "bot", text: "Welcome to the TUM Onboarding Assistant!" },
					{
						role: "bot",
						text: "Hello! I am the TUM Chat-bot Onboarding Assistant. I can help you get right on track with your research aspirations at TUM. What is your role in the University and what step of the process are you in?",
					},
				]);
			}
		} catch (error) {
			console.error("Error initializing session:", error);
			setMessages([
				{ role: "bot", text: "Welcome to the TUM Onboarding Assistant!" },
				{
					role: "bot",
					text: "Hello! I am the TUM Chat-bot Onboarding Assistant. I can help you get right on track with your research aspirations at TUM. What is your role in the University and what step of the process are you in?",
				},
			]);
		}
	};

	const sendMessage = async () => {
		if (!input.trim() || isLoading) return;

		const userMessage = { role: "user", text: input };
		setMessages((prev) => [...prev, userMessage]);
		setInput("");
		setIsLoading(true);

		try {
			const response = await fetch(`${API_BASE_URL}/api/chat`, {
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
			setMessages((prev) => [
				...prev,
				{
					role: "bot",
					text: "I apologize, but I'm having trouble connecting to the server. Please check your internet connection and try again.",
				},
			]);
		} finally {
			setIsLoading(false);
		}
	};

	const handleCopy = (text, index) => {
		navigator.clipboard.writeText(text).then(() => {
			setCopiedIndex(index);
			setTimeout(() => setCopiedIndex(null), 2000);
		});
	};

	const handleAttachClick = () => fileInputRef.current.click();

	const handleFileChange = (event) => {
		const file = event.target.files[0];
		if (file) {
			const fileMessage = { role: "user", text: `Attached: ${file.name}` };
			setMessages((prev) => [...prev, fileMessage]);
			event.target.value = null;
		}
	};

	// Cleanup session on component unmount
	useEffect(() => {
		return () => {
			if (sessionId) {
				fetch(`${API_BASE_URL}/api/session/${sessionId}/end`, {
					method: "POST",
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
			<header className="chat-header-internal">
				<img
					src="/tum-logo.png"
					alt="TUM Logo"
					className="chat-logo-internal"
				/>
			</header>

			<div className="messages">
				{messages.map((msg, i) => (
					<div key={i} className={`message-container ${msg.role}`}>
						<div className={`message-bubble ${msg.role}`}>
							<span>{msg.text}</span>
							{msg.role === "bot" && (
								<button
									onClick={() => handleCopy(msg.text, i)}
									className="copy-button"
									title="Copy to clipboard"
								>
									{copiedIndex === i ? "✅" : "📋"}
								</button>
							)}
						</div>
					</div>
				))}
				{isLoading && (
					<div className="message-container bot">
						<div className="message-bubble bot">
							<span>Thinking...</span>
						</div>
					</div>
				)}
			</div>

			<div className="input-bar">
				<button className="attach-button" onClick={handleAttachClick}>
					+
				</button>
				<input
					type="file"
					ref={fileInputRef}
					style={{ display: "none" }}
					onChange={handleFileChange}
					accept="application/pdf,image/jpeg,image/png"
				/>
				<input
					className="input-field"
					value={input}
					onChange={(e) => setInput(e.target.value)}
					onKeyDown={(e) => e.key === "Enter" && !isLoading && sendMessage()}
					placeholder="Ask me anything..."
					disabled={isLoading}
				/>
				<button
					className="send-button"
					onClick={sendMessage}
					disabled={isLoading || !input.trim()}
				>
					{isLoading ? "Sending..." : "Send"}
				</button>
			</div>

			<div className="action-links">
				<a href="mailto:onboarding-support@tum.de" className="action-link">
					Ask for Help
				</a>
				<a
					href="https://your-suggestion-form-url.com"
					target="_blank"
					rel="noopener noreferrer"
					className="action-link"
				>
					Suggest Improvement
				</a>
			</div>
		</div>
	);
}
