export default function ChatMessage({ message, isOwn }) {
  const initials = message.user.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  const time = new Date(message.created_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className={`flex gap-2 ${isOwn ? "flex-row-reverse" : ""}`}>
      <div
        className={`w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-semibold ${
          isOwn ? "bg-brand-100 text-brand-700" : "bg-gray-100 text-gray-600"
        }`}
      >
        {initials}
      </div>
      <div className={`max-w-[70%] ${isOwn ? "items-end" : "items-start"} flex flex-col`}>
        <div
          className={`px-3 py-2 rounded-2xl text-sm ${
            isOwn
              ? "bg-brand-600 text-white rounded-tr-sm"
              : "bg-gray-100 text-gray-800 rounded-tl-sm"
          }`}
        >
          {message.text}
        </div>
        <span className="text-xs text-gray-400 mt-0.5 px-1">
          {!isOwn && <span className="font-medium mr-1">{message.user.name}</span>}
          {time}
        </span>
      </div>
    </div>
  );
}
