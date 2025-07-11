import { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import ChatWindow from "./components/ChatWindow.jsx";
import InfoSidebar from "./components/InfoSidebar.jsx";
import DarkModeToggle from "./components/DarkModeToggle.jsx";
import SecurityGuard from "./components/SecurityGuard.jsx";

// Dark Mode Context
const DarkModeContext = createContext();

export const useDarkMode = () => {
	const context = useContext(DarkModeContext);
	if (!context) {
		throw new Error("useDarkMode must be used within a DarkModeProvider");
	}
	return context;
};

export default function App() {
	const [isDarkMode, setIsDarkMode] = useState(() => {
		// Check localStorage first, then system preference
		const saved = localStorage.getItem("darkMode");
		if (saved !== null) {
			return JSON.parse(saved);
		}
		return window.matchMedia("(prefers-color-scheme: dark)").matches;
	});

	const [showSidebar, setShowSidebar] = useState(false);

	useEffect(() => {
		localStorage.setItem("darkMode", JSON.stringify(isDarkMode));
		if (isDarkMode) {
			document.documentElement.classList.add("dark");
		} else {
			document.documentElement.classList.remove("dark");
		}
	}, [isDarkMode]);

	const toggleDarkMode = () => {
		setIsDarkMode(!isDarkMode);
	};

	const toggleSidebar = () => {
		setShowSidebar(!showSidebar);
	};

	return (
		<DarkModeContext.Provider value={{ isDarkMode, toggleDarkMode }}>
			<SecurityGuard>
				<div className={`app-wrapper ${isDarkMode ? "dark" : ""}`}>
					<header className="mobile-header">
						<button
							onClick={toggleSidebar}
							className="sidebar-toggle"
							aria-label="Toggle sidebar"
						>
							<svg
								width="24"
								height="24"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								strokeWidth="2"
							>
								<line x1="3" y1="6" x2="21" y2="6" />
								<line x1="3" y1="12" x2="21" y2="12" />
								<line x1="3" y1="18" x2="21" y2="18" />
							</svg>
						</button>
						<h1 className="app-title">TUM Chatbot</h1>
						<img
							src="/tum-logo.png"
							alt="TUM Logo"
							className="header-logo-mobile"
						/>
						<div style={{ width: "44px", height: "44px" }}></div>
					</header>

					<main className="main-content">
						<InfoSidebar
							isOpen={showSidebar}
							onClose={() => setShowSidebar(false)}
						/>
						<div className="chat-container">
							<ChatWindow />
						</div>
					</main>

					{/* Overlay for mobile sidebar */}
					{showSidebar && (
						<div
							className="sidebar-overlay"
							onClick={() => setShowSidebar(false)}
						/>
					)}
				</div>
			</SecurityGuard>
		</DarkModeContext.Provider>
	);
}
