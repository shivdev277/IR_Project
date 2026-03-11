import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [course, setCourse] = useState("NETSEC");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await axios.post("http://127.0.0.1:8000/search", {
        course,
        query,
      });
      setResults(response.data.results ?? []);
    } catch (err) {
      if (err.response) {
        setError(`Server error: ${err.response.status} — ${err.response.data?.detail ?? "Unknown error"}`);
      } else if (err.request) {
        setError("Could not reach the backend. Make sure the server is running on http://127.0.0.1:8000.");
      } else {
        setError(`Unexpected error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="container">
        <h1 className="title">College Semantic Search System</h1>

        <div className="form-group">
          <label htmlFor="course-select" className="label">
            Select Course
          </label>
          <select
            id="course-select"
            className="select"
            value={course}
            onChange={(e) => setCourse(e.target.value)}
          >
            <option value="NETSEC">NETSEC</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="query-input" className="label">
            Enter your question
          </label>
          <input
            id="query-input"
            type="text"
            className="input"
            placeholder="e.g. What is a firewall?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
        </div>

        <button
          className="search-btn"
          onClick={handleSearch}
          disabled={!query.trim() || loading}
        >
          {loading ? "Searching..." : "Search"}
        </button>

        <div className="results-area">
          {loading && (
            <p className="results-placeholder">Searching...</p>
          )}

          {error && !loading && (
            <p className="results-error">{error}</p>
          )}

          {!loading && !error && results.length === 0 && (
            <p className="results-placeholder">
              Results will appear here after you search.
            </p>
          )}

          {!loading && results.length > 0 && (
            <ul className="results-list">
              {results.map((result, index) => (
                <li key={index} className="result-card">
                  <p className="result-answer"><strong>Answer:</strong> {result.answer}</p>
                  <p className="result-meta"><strong>File:</strong> {result.file}</p>
                  <p className="result-meta">
                    <strong>{result.page != null ? "Page" : "Slide"}:</strong>{" "}
                    {result.page ?? result.slide}
                  </p>
                  <p className="result-meta">
                    <strong>Similarity Score:</strong>{" "}
                    {typeof result.score === "number" ? result.score.toFixed(4) : result.score}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
