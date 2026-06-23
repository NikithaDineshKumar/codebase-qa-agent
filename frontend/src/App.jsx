import { useState } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [sources, setSources] = useState([]);
  const [isIngesting, setIsIngesting] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const [indexedRepo, setIndexedRepo] = useState(null);
  const [totalChunks, setTotalChunks] = useState(0);

  const handleIngest = async () => {
    if (!repoUrl.trim()) return;
    setIsIngesting(true);
    setMessages([]);
    setSources([]);
    try {
      const res = await axios.post(`${API_BASE}/ingest`, {
        github_url: repoUrl,
      });
      setIndexedRepo(repoUrl);
      setTotalChunks(res.data.total_chunks);
      setMessages([
        {
          role: "system",
          text: `✅ Successfully indexed ${res.data.total_chunks} code chunks from ${repoUrl}. Ask me anything about this codebase!`,
        },
      ]);
    } catch (err) {
      setMessages([
        {
          role: "system",
          text: `❌ Error: ${err.response?.data?.detail || err.message}`,
        },
      ]);
    }
    setIsIngesting(false);
  };

  const handleQuery = async () => {
    if (!question.trim() || !indexedRepo) return;
    const userMessage = { role: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setIsQuerying(true);
    setSources([]);
    try {
      const res = await axios.post(`${API_BASE}/query`, {
        question: question,
        top_k: 5,
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: res.data.answer },
      ]);
      setSources(res.data.sources);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: `❌ Error: ${err.response?.data?.detail || err.message}`,
        },
      ]);
    }
    setIsQuerying(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
            Q
          </div>
          <h1 className="text-xl font-bold text-white">Codebase Q&A Agent</h1>
        </div>
        {indexedRepo && (
          <div className="flex items-center gap-2 bg-green-900/30 border border-green-700 rounded-lg px-3 py-1">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span className="text-green-400 text-sm font-medium">
              {totalChunks} chunks indexed
            </span>
          </div>
        )}
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Repo Input + Sources */}
        <div className="w-80 bg-gray-900 border-r border-gray-800 flex flex-col p-4 gap-4">
          {/* Repo Input */}
          <div>
            <label className="text-sm font-medium text-gray-400 mb-2 block">
              GitHub Repository URL
            </label>
            <input
              type="text"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/user/repo"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
            <button
              onClick={handleIngest}
              disabled={isIngesting || !repoUrl.trim()}
              className="mt-2 w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 text-white font-medium py-2 px-4 rounded-lg text-sm transition-colors"
            >
              {isIngesting ? "Indexing..." : "Index Repository"}
            </button>
          </div>

          {/* Indexed Repo Info */}
          {indexedRepo && (
            <div className="bg-gray-800 rounded-lg p-3">
              <p className="text-xs text-gray-400 mb-1">Currently indexed:</p>
              <p className="text-xs text-blue-400 break-all">{indexedRepo}</p>
            </div>
          )}

          {/* Sources Panel */}
          {sources.length > 0 && (
            <div className="flex-1 overflow-y-auto">
              <p className="text-sm font-medium text-gray-400 mb-2">
                Sources Used
              </p>
              <div className="flex flex-col gap-2">
                {sources.map((src, i) => (
                  <div
                    key={i}
                    className="bg-gray-800 rounded-lg p-3 border border-gray-700"
                  >
                    <p className="text-xs font-mono text-blue-400 break-all">
                      {src.file_path.split("\\").pop().split("/").pop()}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Lines {src.start_line}–{src.end_line}
                    </p>
                    <p className="text-xs text-gray-500">
                      {src.chunk_type}: {src.name}
                    </p>
                    <p className="text-xs text-green-400 mt-1">
                      Score: {src.rrf_score}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - Chat */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
            {messages.length === 0 && (
              <div className="flex-1 flex flex-col items-center justify-center text-center gap-4">
                <div className="w-16 h-16 bg-blue-600/20 rounded-2xl flex items-center justify-center">
                  <span className="text-3xl">🔍</span>
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-white mb-2">
                    Ask anything about your codebase
                  </h2>
                  <p className="text-gray-500 text-sm max-w-md">
                    Paste a GitHub URL on the left, click Index Repository, then
                    ask questions like "How does authentication work?" or
                    "Explain the database models"
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 justify-center mt-2">
                  {[
                    "How does routing work?",
                    "What are the main classes?",
                    "Explain the database models",
                    "Where is authentication handled?",
                  ].map((q) => (
                    <button
                      key={q}
                      onClick={() => setQuestion(q)}
                      className="bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs px-3 py-2 rounded-lg border border-gray-700 transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-3xl rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                    msg.role === "user"
                      ? "bg-blue-600 text-white rounded-br-sm"
                      : msg.role === "system"
                        ? "bg-gray-800 text-gray-300 border border-gray-700 w-full"
                        : "bg-gray-800 text-gray-100 rounded-bl-sm"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}

            {isQuerying && (
              <div className="flex justify-start">
                <div className="bg-gray-800 rounded-2xl rounded-bl-sm px-4 py-3">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t border-gray-800 p-4">
            <div className="flex gap-3 items-end">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={
                  indexedRepo
                    ? "Ask a question about the codebase... (Enter to send)"
                    : "Index a repository first..."
                }
                disabled={!indexedRepo || isQuerying}
                rows={2}
                className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none disabled:opacity-50"
              />
              <button
                onClick={handleQuery}
                disabled={!indexedRepo || isQuerying || !question.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 text-white font-medium py-3 px-5 rounded-xl text-sm transition-colors"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}