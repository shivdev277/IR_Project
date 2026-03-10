import { useState } from "react";
import "./App.css";

function App() {
  const [course, setCourse] = useState("NETSEC");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);

  const handleSearch = () => {
    // Backend connection will be added later
    console.log("Searching for:", query, "in course:", course);
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
          disabled={!query.trim()}
        >
          Search
        </button>

        <div className="results-area">
          {results.length === 0 && (
            <p className="results-placeholder">
              Results will appear here after you search.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
