import React, { useState } from 'react';
import { useMutation } from 'react-query';
import { smartSearch } from '../services/api';
import './SmartSearch.css';

const SmartSearch = ({ onCandidateClick }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [hasSearched, setHasSearched] = useState(false);

    const mutation = useMutation(
        (q) => smartSearch({ query: q }),
        {
            onSuccess: (data) => {
                setResults(data.data.results);
                setHasSearched(true);
            },
            onError: (err) => {
                setResults([]);
                setHasSearched(true);
                console.error("Search error:", err);
                alert("Error during deep search. Please check your connection and try again.");
            }
        }
    );

    const handleSearch = (e) => {
        e.preventDefault();
        if (query.trim()) {
            setHasSearched(false);
            mutation.mutate(query);
        }
    };

    return (
        <div className="smart-search-container">
            <form onSubmit={handleSearch} className="search-form">
                <input
                    type="text"
                    placeholder="e.g. 'Senior Python developers with AWS experience'..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="search-input"
                />
                <button type="submit" className="btn-search" disabled={mutation.isLoading}>
                    {mutation.isLoading ? 'Deep Searching...' : '🔍 Smart Search'}
                </button>
            </form>

            {(results.length > 0 || (hasSearched && !mutation.isLoading)) && (
                <div className="search-results-overlay">
                    <div className="results-list">
                        <div className="results-header">
                            <h4>Matches for "{query}"</h4>
                            <button className="btn-close-results" onClick={() => { setResults([]); setHasSearched(false); }}>&times;</button>
                        </div>
                        {results.length > 0 ? results.map(cand => (
                            <div key={cand.id} className="search-result-item" onClick={() => onCandidateClick(cand)}>
                                <div className="result-info">
                                    <span className="result-name">{cand.name}</span>
                                    <span className="result-exp">{cand.experience_years || 0} yrs exp</span>
                                </div>
                                <div className="result-score">
                                    {(cand.score * 100).toFixed(0)}%
                                </div>
                            </div>
                        )) : (
                            <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                                No candidates found matching your criteria. Try adjusting your search.
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default SmartSearch;
