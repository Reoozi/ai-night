"use client";
import { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
}

interface RetrievalResult {
  id: number;
  content: string;
  metadata: Record<string, any>;
  similarity_score: number;
  rerank_score?: number;
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<"search" | "upload">("search");
  const [messages, setMessages] = useState<Message[]>([
    { role: "system", content: "🔍 RAG Semantic Search System Ready" },
  ]);

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<RetrievalResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Upload state
  const [uploadText, setUploadText] = useState("");
  const [documentTitle, setDocumentTitle] = useState("");
  const [documentCategory, setDocumentCategory] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  // General state
  const [useReranker, setUseReranker] = useState(true);
  const [stats, setStats] = useState({
    total_documents: 0,
    embedding_model: "",
    embedding_dimension: 0,
  });
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const { data } = await axios.get("http://127.0.0.1:8000/rag/stats");
      setStats(data);
    } catch (error) {
      console.log("Stats unavailable (database may not be running)");
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim() || isSearching) return;

    setMessages((prev) => [...prev, { role: "user", content: searchQuery }]);
    setIsSearching(true);

    try {
      const { data } = await axios.post("http://127.0.0.1:8000/rag/search", {
        query: searchQuery,
        top_k: 3,
        use_reranker: useReranker,
      });

      if (data.status === "success") {
        setSearchResults(data.results);
        setMessages((prev) => [
          ...prev,
          {
            role: "system",
            content: `✅ Found ${data.results_count} relevant fragments${useReranker ? " (reranked)" : ""}`,
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "system", content: `❌ Error: ${data.message}` },
        ]);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: "❌ Connection error. Make sure the backend is running.",
        },
      ]);
    } finally {
      setIsSearching(false);
      setSearchQuery("");
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadText.trim() || isUploading) return;

    setIsUploading(true);

    try {
      const { data } = await axios.post("http://127.0.0.1:8000/rag/index", {
        documents: [
          {
            content: uploadText,
            title: documentTitle || "Untitled",
            category: documentCategory || "General",
            metadata: { timestamp: new Date().toISOString() },
          },
        ],
        use_reranker: false,
      });

      if (data.status === "success") {
        setMessages((prev) => [
          ...prev,
          {
            role: "system",
            content: `✅ Indexed: ${data.total_chunks} chunks from 1 document. Total in DB: ${data.document_count_in_db}`,
          },
        ]);
        setUploadText("");
        setDocumentTitle("");
        setDocumentCategory("");
        fetchStats();
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "system", content: `❌ Error: ${data.message}` },
        ]);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: "❌ Upload failed. Make sure the backend is running.",
        },
      ]);
    } finally {
      setIsUploading(false);
    }
  };

  const handleClearDB = async () => {
    if (
      !window.confirm(
        "Are you sure you want to delete all documents? This cannot be undone.",
      )
    )
      return;

    try {
      await axios.delete("http://127.0.0.1:8000/rag/clear");
      setMessages((prev) => [
        ...prev,
        { role: "system", content: "🗑️ All documents cleared" },
      ]);
      setSearchResults([]);
      fetchStats();
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "system", content: "❌ Clear failed" },
      ]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      {/* Header */}
      <header className="border-b border-indigo-100 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                🔍 RAG Search System
              </h1>
              <p className="text-sm text-slate-500 mt-1">
                Semantic Search with Document Intelligence
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-xs text-slate-500">Documents Indexed</div>
                <div className="text-2xl font-bold text-indigo-600">
                  {stats.total_documents}
                </div>
              </div>
              <div className="w-px h-12 bg-slate-200"></div>
              <div className="text-right">
                <div className="text-xs text-slate-500">Model</div>
                <div className="text-sm font-mono text-slate-700">
                  {stats.embedding_model || "loading..."}
                </div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2">
            <button
              onClick={() => {
                setActiveTab("search");
                setSearchResults([]);
              }}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === "search"
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              🔎 Search Documents
            </button>
            <button
              onClick={() => setActiveTab("upload")}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === "upload"
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              📤 Upload & Index
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {activeTab === "search" ? (
          <div className="space-y-6">
            {/* Search Form */}
            <form
              onSubmit={handleSearch}
              className="bg-white rounded-2xl shadow-lg p-8 border border-indigo-100"
            >
              <label className="block text-sm font-semibold text-slate-700 mb-4">
                Ask a question about your documents:
              </label>
              <div className="flex gap-3 mb-4">
                <input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="e.g., What are the leave policies? Or: When is salary paid?"
                  className="flex-1 px-5 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                <button
                  type="submit"
                  disabled={isSearching}
                  className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium rounded-xl hover:shadow-lg hover:shadow-indigo-300 active:scale-95 transition-all disabled:opacity-50"
                >
                  {isSearching ? "⏳ Searching..." : "🔍 Search"}
                </button>
              </div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useReranker}
                  onChange={(e) => setUseReranker(e.target.checked)}
                  className="w-4 h-4 accent-indigo-600"
                />
                <span className="text-sm text-slate-600">
                  Use reranking (improves relevance)
                </span>
              </label>
            </form>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="space-y-4">
                <h2 className="text-xl font-bold text-slate-900">
                  Top 3 Results
                </h2>
                {searchResults.map((result, index) => (
                  <div
                    key={result.id}
                    className="bg-white rounded-xl shadow-md p-6 border-l-4 border-indigo-500 hover:shadow-lg transition-shadow"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-bold text-lg text-slate-900">
                          #{index + 1} -{" "}
                          {result.metadata?.title || `Document ${result.id}`}
                        </h3>
                        {result.metadata?.category && (
                          <span className="inline-block mt-1 px-2 py-1 bg-indigo-100 text-indigo-700 text-xs rounded-md">
                            {result.metadata.category}
                          </span>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-slate-500">
                          Similarity Score
                        </div>
                        <div className="text-2xl font-bold text-indigo-600">
                          {(result.similarity_score * 100).toFixed(1)}%
                        </div>
                        {result.rerank_score !== undefined && (
                          <>
                            <div className="text-xs text-slate-500 mt-2">
                              Rerank Score
                            </div>
                            <div className="text-lg font-bold text-purple-600">
                              {result.rerank_score?.toFixed(2) || "N/A"}
                            </div>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Score Bar */}
                    <div className="mb-4">
                      <div className="w-full bg-slate-200 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-indigo-500 to-purple-500 h-2 rounded-full transition-all"
                          style={{ width: `${result.similarity_score * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Content */}
                    <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                      <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
                        {result.content.length > 400
                          ? result.content.substring(0, 400) + "..."
                          : result.content}
                      </p>
                    </div>

                    {result.metadata?.source && (
                      <div className="text-xs text-slate-500 mt-3">
                        📄 Source: {result.metadata.source}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Messages Log */}
            <div className="bg-white rounded-xl shadow-md p-6 max-h-64 overflow-y-auto">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`mb-3 flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`px-3 py-2 rounded-lg text-sm ${
                      msg.role === "user"
                        ? "bg-indigo-100 text-indigo-900"
                        : msg.role === "system"
                          ? "bg-purple-100 text-purple-900"
                          : "bg-slate-100 text-slate-900"
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              <div ref={scrollRef} />
            </div>
          </div>
        ) : (
          /* Upload Tab */
          <div className="max-w-2xl mx-auto">
            <form
              onSubmit={handleUpload}
              className="bg-white rounded-2xl shadow-lg p-8 border border-indigo-100"
            >
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Document Title
                  </label>
                  <input
                    value={documentTitle}
                    onChange={(e) => setDocumentTitle(e.target.value)}
                    placeholder="e.g., Leave Policies, Finance Guide"
                    className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Category
                  </label>
                  <input
                    value={documentCategory}
                    onChange={(e) => setDocumentCategory(e.target.value)}
                    placeholder="e.g., HR, Finance, Procedures"
                    className="w-full px-4 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Document Content
                  </label>
                  <textarea
                    value={uploadText}
                    onChange={(e) => setUploadText(e.target.value)}
                    placeholder="Paste your document content here..."
                    rows={10}
                    className="w-full px-4 py-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-sm"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isUploading}
                  className="w-full px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-indigo-300 active:scale-95 transition-all disabled:opacity-50"
                >
                  {isUploading ? "⏳ Indexing..." : "📤 Index Document"}
                </button>
              </div>
            </form>

            {/* Messages Log */}
            <div className="bg-white rounded-xl shadow-md p-6 mt-6 max-h-64 overflow-y-auto">
              {messages.map((msg, i) => (
                <div key={i} className="mb-3">
                  <div
                    className={`px-3 py-2 rounded-lg text-sm ${
                      msg.role === "system"
                        ? "bg-purple-100 text-purple-900"
                        : "bg-slate-100 text-slate-900"
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              <div ref={scrollRef} />
            </div>

            {/* Danger Zone */}
            <div className="mt-8 p-6 bg-red-50 border border-red-200 rounded-xl">
              <h3 className="font-bold text-red-900 mb-3">⚠️ Danger Zone</h3>
              <button
                onClick={handleClearDB}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
              >
                Delete All Documents
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
