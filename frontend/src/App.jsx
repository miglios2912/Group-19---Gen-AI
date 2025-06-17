import './App.css'; // or ChatWindow.css
import ChatWindow from './components/ChatWindow';

export default function App() {
  return (
    <div className="chat-wrapper">
      <header className="chat-header">
        <img src="/TUM_logo.png" alt="TUM Logo" className="chat-logo" />
      </header>

      <main>
        <div className="chat-container">
          <ChatWindow />
        </div>
      </main>
    </div>
  );
}
