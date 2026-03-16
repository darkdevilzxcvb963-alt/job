import React, { useState } from 'react';
import { useMutation } from 'react-query';
import { generateInterviewPrep } from '../services/api';
import './InterviewSimulator.css';

const InterviewSimulator = ({ jobTitle, candidateSkills, jobRequirements, onClose }) => {
    const [questions, setQuestions] = useState([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(-1);

    const mutation = useMutation(
        () => generateInterviewPrep({
            candidate_skills: candidateSkills,
            job_requirements: jobRequirements,
            job_title: jobTitle
        }),
        {
            onSuccess: (data) => {
                setQuestions(data.data.questions);
                setCurrentQuestionIndex(0);
            }
        }
    );

    const handleStart = () => {
        mutation.mutate();
    };

    return (
        <div className="interview-modal-overlay">
            <div className="interview-modal-content">
                <button className="close-button" onClick={onClose}>&times;</button>

                <div className="interview-header">
                    <h2>🎤 AI Interview Simulator</h2>
                    <p>Practicing for <strong>{jobTitle}</strong></p>
                </div>

                {currentQuestionIndex === -1 ? (
                    <div className="prep-start">
                        <div className="prep-info">
                            <p>Our AI will analyze the job requirements and your skills to generate 5 tailored questions.</p>
                            <div className="focus-areas">
                                <span>🎯 Skill Gaps</span>
                                <span>💡 Technical Depth</span>
                                <span>🤝 Culture Fit</span>
                            </div>
                        </div>
                        <button
                            className="btn-start-prep"
                            onClick={handleStart}
                            disabled={mutation.isLoading}
                        >
                            {mutation.isLoading ? 'Generating Questions...' : 'Start Simulation'}
                        </button>
                    </div>
                ) : (
                    <div className="question-flow">
                        <div className="progress-bar">
                            <div
                                className="progress-fill"
                                style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
                            ></div>
                        </div>

                        <div className="question-card">
                            <span className="question-number">Question {currentQuestionIndex + 1} of {questions.length}</span>
                            <h3 className="question-text">{questions[currentQuestionIndex]}</h3>

                            <div className="user-response-area">
                                <textarea placeholder="Type your notes or bullet points here for practice..." rows="5"></textarea>
                            </div>
                        </div>

                        <div className="flow-controls">
                            <button
                                className="btn-secondary"
                                disabled={currentQuestionIndex === 0}
                                onClick={() => setCurrentQuestionIndex(prev => prev - 1)}
                            >
                                Previous
                            </button>

                            {currentQuestionIndex < questions.length - 1 ? (
                                <button
                                    className="btn-primary"
                                    onClick={() => setCurrentQuestionIndex(prev => prev + 1)}
                                >
                                    Next Question
                                </button>
                            ) : (
                                <button className="btn-finish" onClick={onClose}>Finish Session</button>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default InterviewSimulator;
