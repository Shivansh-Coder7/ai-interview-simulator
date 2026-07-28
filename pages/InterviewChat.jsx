import { useEffect, useRef, useState } from "react";
import { useLocation, useParams, useNavigate } from "react-router-dom";
import api from "../api";

export default function InterviewChat() {
  const { sessionId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [finished, setFinished] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    const firstQuestion = location.state?.firstQuestion;
    if (firstQuestion) {
      setMessages([{ role: "ai", text: firstQuestion }]);
    }
  }, [location.state]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendAnswer = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.post("/interview/answer", {
        session_id: Number(sessionId),
        answer: userMsg.text,
      });

      if (res.data.finished) {
        setFinished(true);
        await api.post(`/interview/finish?session_id=${sessionId}`);
        setMessages((prev) => [
          ...prev,
          { role: "ai", text: "That's the end of the interview. Generating your report..." },
        ]);
        setTimeout(() => navigate(`/report/${sessionId}`), 1200);
      } else {
        setMessages((prev) => [...prev, { role: "ai", text: res.data.question }]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: "Something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendAnswer();
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <div className="bg-white shadow-sm px-6 py-4">
        <h1 className="font-semibold text-slate-800">Interview in progress</h1>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3 max-w-2xl mx-auto w-full">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[75%] px-4 py-2 rounded-2xl text-sm ${
                m.role === "user"
                  ? "bg-indigo-600 text-white rounded-br-sm"
                  : "bg-white shadow-sm text-slate-800 rounded-bl-sm"
              }`}
            >
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white shadow-sm text-slate-400 text-sm px-4 py-2 rounded-2xl rounded-bl-sm">
              Typing...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {!finished && (
        <div className="border-t bg-white px-6 py-4">
          <div className="max-w-2xl mx-auto flex gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your answer..."
              rows={2}
              className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm resize-none"
            />
            <button
              onClick={sendAnswer}
              disabled={loading}
              className="bg-indigo-600 text-white px-5 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
