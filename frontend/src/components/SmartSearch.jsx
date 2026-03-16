import React, { useState } from 'react';
import { useMutation } from 'react-query';
import { smartSearch } from '../services/api';
import './SmartSearch.css';

const SmartSearch = ({ onCandidateClick }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);

    const mutation = useMutation(
        (q) => smartSearch({ query: q }),
        {
            onSuccess: (data) => {
                setResults(data.data.results);
            }
        }
    );

    const handleSearch = (e) => {
        e.preventDefault();
        if (query.trim()) {
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

            {results.length > 0 && (
                <div className="search-results-overlay">
                    <div className="results-list">
                        <div className="results-header">
                            <h4>Matches for "{query}"</h4>
                            <button className="btn-close-results" onClick={() => setResults([])}>&times;</button>
                        </div>
                        {results.map(cand => (
                            <div key={cand.id} className="search-result-item" onClick={() => onCandidateClick(cand)}>
                                <div className="result-info">
                                    <span className="result-name">{cand.name}</span>
                                    <span className="result-exp">{cand.experience_years || 0} yrs exp</span>
                                </div>
                                <div className="result-score">
                                    {(cand.score * 100).toFixed(0)}%
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default SmartSearch;
