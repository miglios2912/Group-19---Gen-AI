import ChatWindow from "./components/ChatWindow";

export default function App() {
  return (
    <div className="min-h-screen bg-iceblue font-sans flex flex-col">
      {/* Header */}
      <header className="bg-white p-4 flex justify-center shadow-md">
        <img src="/tum-logo.png" alt="TUM Logo" className="h-14" />
      </header>
      <div className="bg-red-500 text-white p-4 text-center">
  ✅ Tailwind is actually working — ignore VS Code!
</div>


      {/* Main Chat Card */}
      <main className="flex-1 flex justify-center items-center px-4 py-12">
        <div className="w-full max-w-2xl bg-white rounded-2xl shadow-xl border border-gray-200 p-4">
          <ChatWindow />
        </div>
      </main>
    </div>
  );
}
