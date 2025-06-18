import './App.css';
import ChatWindow from './components/ChatWindow.jsx'; // Using .jsx
import InfoSidebar from './components/InfoSidebar.jsx'; // Using .jsx

export default function App() {
  return (
    <div className="app-wrapper">
      {/* The main header has been removed */}
      <main className="main-content">
        <InfoSidebar />
        <div className="chat-container">
          <ChatWindow />
        </div>
      </main>
    </div>
  );
}