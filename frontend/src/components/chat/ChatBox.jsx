import { useState, useEffect, useRef, useCallback } from "react";
import { useAuth } from "../../context/AuthContext";
import ChatMessage from "./ChatMessage";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

export default function ChatBox({ expenseId }) {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const bottomRef = useRef(null);

  const connect = useCallback(() => {
    const token = localStorage.getItem("access_token");
    const ws = new WebSocket(`${WS_URL}/ws/expenses/${expenseId}/?token=${token}`);

    ws.onopen = () => setConnected(true);
    ws.onclose = () => {
      setConnected(false);
      // Reconnect after 3s
      setTimeout(connect, 3000);
    };
    ws.onerror = () => ws.close();
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "chat.history") {
        setMessages(data.messages);
      } else if (data.type === "chat.message") {
        setMessages((prev) => [...prev, data.message]);
      }
    };

    wsRef.current = ws;
  }, [expenseId]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = (e) => {
    e.preventDefault();
    if (!text.trim() || !connected) return;
    wsRef.current?.send(JSON.stringify({ type: "chat.message", text: text.trim() }));
    setText("");
  };

  return (
    <div className="flex flex-col h-80 border border-gray-200 rounded-xl overflow-hidden">
      <div className="bg-gray-50 px-4 py-2.5 border-b flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${connected ? "bg-green-500" : "bg-gray-300"}`} />
        <span className="text-sm font-medium text-gray-700">
          {connected ? "Live chat" : "Connecting..."}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-white">
        {messages.length === 0 && (
          <p className="text-xs text-gray-400 text-center py-4">
            No messages yet. Start the conversation!
          </p>
        )}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} isOwn={msg.user.id === user?.id} />
        ))}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={sendMessage} className="flex gap-2 p-3 border-t bg-white">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="input flex-1 text-sm"
          placeholder="Type a message..."
          disabled={!connected}
        />
        <button
          type="submit"
          disabled={!text.trim() || !connected}
          className="btn-primary px-4 text-sm"
        >
          Send
        </button>
      </form>
    </div>
  );
}
