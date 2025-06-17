import ChatWindow from "./components/ChatWindow";

function App() {
  return (
    <div className="h-screen bg-gray-100 flex items-center justify-center">
      <div className="w-full max-w-2xl h-[90vh] bg-white shadow-lg rounded-xl">
        <ChatWindow />
      </div>
    </div>
  );
}

export default App;
