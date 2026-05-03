import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/search";

function App() {
  const [course, setCourse] = useState("NETSEC");
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const getLocationLabel = (fileName = "") => {
    const lower = fileName.toLowerCase();
    if (lower.endsWith(".ppt") || lower.endsWith(".pptx")) {
      return "Slide";
    }
    return "Page";
  };

  const handleSearch = async () => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery) return;

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        id: `${Date.now()}-user`,
        content: trimmedQuery,
      },
    ]);
    setQuery("");

    setLoading(true);

    try {
      const response = await axios.post(API_URL, {
        course,
        query: trimmedQuery,
      });

      const answerText = response.data?.answer ?? "No matching result found.";
      const backendResults = Array.isArray(response.data?.results)
        ? response.data.results
        : [];

      if (backendResults.length === 0) {
        setMessages((prev) => [
          ...prev,
          {
            role: "system",
            id: `${Date.now()}-system-empty`,
            answer: answerText,
            results: [],
          },
        ]);
      } else {
        const rankedResults = backendResults.slice(0, 3).map((result, index) => ({
          rank: index + 1,
          file: result.file ?? "Unknown",
          page: result.page ?? "N/A",
          score: typeof result.score === "number" ? result.score.toFixed(4) : (result.score ?? "N/A"),
          bm25: typeof result.bm25 === "number" ? result.bm25.toFixed(4) : (result.bm25 ?? "N/A"),
          cosine: typeof result.cosine === "number" ? result.cosine.toFixed(4) : (result.cosine ?? "N/A"),
          locationLabel: getLocationLabel(result.file),
        }));

        const systemMessage = {
          role: "system",
          id: `${Date.now()}-system-top3`,
          answer: answerText,
          results: rankedResults,
        };

        setMessages((prev) => [...prev, systemMessage]);
      }
    } catch (err) {
      let message = "Unexpected error. Please try again.";

      if (err.response) {
        message = `Server error: ${err.response.status} - ${err.response.data?.detail ?? "Unknown error"}`;
      } else if (err.request) {
        message = "Could not reach the backend. Make sure the server is running on http://127.0.0.1:8000.";
      } else if (err.message) {
        message = `Unexpected error: ${err.message}`;
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          id: `${Date.now()}-system-error`,
          answer: message,
          results: [],
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="container">
        <h1 className="title">College Search Assistant</h1>

        <div className="chat-window">
          {messages.length === 0 && !loading && (
            <p className="chat-placeholder">
              Ask a course question to start the conversation.
            </p>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`message-row ${message.role === "user" ? "message-row-user" : "message-row-system"}`}
            >
              <div
                className={`message-bubble ${message.role === "user" ? "user-bubble" : "system-bubble"} ${message.isError ? "error-bubble" : ""}`}
              >
                {message.role === "user" ? (
                  <p className="message-text">{message.content}</p>
                ) : (
                  <>
                    <p className="result-line answer-line"><strong>Answer:</strong> {message.answer}</p>

                    {Array.isArray(message.results) && message.results.length > 0 && (
                      <div className="ranked-results">
                        {message.results.map((result) => (
                          <div key={`${message.id}-${result.rank}`} className="ranked-card">
                            <p className="ranked-title">Rank #{result.rank}</p>
                            <p className="result-line"><strong>File Name:</strong> {result.file}</p>
                            <p className="result-line"><strong>{result.locationLabel}:</strong> {result.page}</p>
                            <p className="result-line"><strong>Final Score:</strong> {result.score}</p>
                            <p className="result-line"><strong>BM25 Score:</strong> {result.bm25}</p>
                            <p className="result-line"><strong>Cosine Score:</strong> {result.cosine}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-row message-row-system">
              <div className="message-bubble system-bubble loading-bubble">Searching...</div>
            </div>
          )}
        </div>

        <div className="controls">
          <div className="form-group">
            <label htmlFor="course-select" className="label">
              Course
            </label>
            <select
              id="course-select"
              className="select"
              value={course}
              onChange={(e) => setCourse(e.target.value)}
            >
              <option value="AI">AI</option>
              <option value="NETSEC">NETSEC</option>
              <option value="IR">IR</option>
              <option value="IR">IR</option>
            </select>
          </div>

          <div className="input-row">
            <input
              id="query-input"
              type="text"
              className="input"
              placeholder="Type your question..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
            <button
              className="search-btn"
              onClick={handleSearch}
              disabled={!query.trim() || loading}
            >
              {loading ? "Searching" : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
