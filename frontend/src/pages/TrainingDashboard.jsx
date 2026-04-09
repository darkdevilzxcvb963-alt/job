import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { 
  BookOpen, 
  Brain, 
  CheckCircle2, 
  ChevronRight, 
  Cpu, 
  FileText, 
  GraduationCap, 
  Layout, 
  Lightbulb, 
  LineChart, 
  MessageSquare, 
  Target, 
  Trophy,
  Loader2,
  AlertCircle,
  Calendar,
  Zap,
  RefreshCw
} from 'lucide-react';
import { useNotify } from '../contexts/NotifyContext';
import '../styles/TrainingDashboard.css';

const TrainingDashboard = () => {
  const { matchId } = useParams();
  const { confirm } = useNotify();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [trainingData, setTrainingData] = useState(null);
  const [activeTab, setActiveTab] = useState('analysis');
  const [answerInput, setAnswerInput] = useState('');
  const [evaluating, setEvaluating] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState('All');
  const [topicAnswers, setTopicAnswers] = useState({});
  const [hasStarted, setHasStarted] = useState(false);
  const [roadmapDays, setRoadmapDays] = useState(14);
  const [quizType, setQuizType] = useState('Mixed');
  const [sessionPoints, setSessionPoints] = useState(0);
  const [roadmapCompleted, setRoadmapCompleted] = useState([]);
  const [roadmapExpanded, setRoadmapExpanded] = useState([]);
  const [selectedQuizTypeFilter, setSelectedQuizTypeFilter] = useState('All');
  const [tasksCompleted, setTasksCompleted] = useState([]);
  const [tasksStarted, setTasksStarted] = useState([]);
  const [topicLoadingMap, setTopicLoadingMap] = useState({});

  const startTraining = () => {
    setHasStarted(true);
    fetchTrainingPlan();
  };

  const fetchTrainingPlan = async (question = null, answer = null) => {
    try {
      if (!answer) setLoading(true);
      setError(null);
      const params = { match_id: matchId, roadmap_days: roadmapDays, quiz_type: quizType, _t: Date.now() };
      if (question) params.question = question;
      if (answer) params.answer = answer;

      const response = await api.post('/training/generate', null, { params });
      
      if (answer) {
        setTrainingData(prev => ({
          ...prev,
          answer_evaluation: response.data.answer_evaluation || null
        }));
      } else {
        const freshData = response.data || {};
        if (!freshData.skill_analysis) freshData.skill_analysis = { level: 'Advanced', missing_skills: [], strengths: [] };
        if (!freshData.roadmap) freshData.roadmap = [];
        
        setTrainingData(freshData);
        if (freshData.questions?.length > 0) {
           setSelectedQuestion(freshData.questions[0]);
        }
      }
      
      if (answer && response.data.answer_evaluation?.score) {
          setSessionPoints(prev => prev + response.data.answer_evaluation.score);
      }
    } catch (err) {
      console.error('CRITICAL: Training Plan Fetch Error:', err);
      setError(err.response?.data?.detail || 'The AI is currently processing many requests. Please try clicking "Start My Pipeline" again or refresh.');
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluateAnswer = async () => {
    if ((!answerInput.trim() && selectedQuestion?.quiz_type !== 'mcq') || !selectedQuestion) return;
    setEvaluating(true);
    await fetchTrainingPlan(selectedQuestion.question, answerInput);
    setEvaluating(false);
    setActiveTab('interview');
  };

  const fetchTopicQuestions = async (topic) => {
    if (!topic || topicLoadingMap[topic]) return;
    
    const hasQuestions = trainingData.questions?.some(q => (q.cat || 'General') === topic);
    if (hasQuestions && trainingData.questions.filter(q => (q.cat || 'General') === topic).length >= 5) {
        return;
    }

    try {
      setTopicLoadingMap(prev => ({ ...prev, [topic]: true }));
      const response = await api.post('/training/generate-questions', null, { 
        params: { 
          topic: topic, 
          job_role: trainingData.job_role || 'Job Role' 
        } 
      });
      
      const newQuestions = response.data.questions || [];
      if (newQuestions.length > 0) {
        setTrainingData(prev => ({
          ...prev,
          questions: [
            ...(prev.questions || []).filter(q => (q.cat || 'General') !== topic),
            ...newQuestions
          ]
        }));
        
        if (selectedTopic === topic || (selectedTopic === 'All' && !selectedQuestion)) {
             setSelectedQuestion(newQuestions[0]);
        }
      }
    } catch (err) {
      console.error(`Failed to fetch questions for ${topic}:`, err);
    } finally {
      setTopicLoadingMap(prev => ({ ...prev, [topic]: false }));
    }
  };

  if (!hasStarted) {
    return (
      <div className="training-setup-container animate-fade-in">
        <div className="card glass">
          <div className="card-header pb-4 mb-6">
            <Zap color="#6366f1" size={20} />
            <h2 className="text-xl font-bold">Configure Your AI Career Coach</h2>
          </div>
          <p className="mb-6 opacity-60">Tailor your custom generated interview and practical roadmap setup.</p>
          
          <div className="setup-group mb-6">
            <label className="block font-medium mb-2">Interview Template Pattern</label>
            <select 
              value={quizType} 
              onChange={e => setQuizType(e.target.value)}
            >
              <option value="Mixed">Mixed (All Types)</option>
              <option value="MCQ">Multiple Choice Only</option>
              <option value="Fill-in-the-Blank">Fill in the Blanks</option>
              <option value="Long Answer">Long Answer Questions</option>
            </select>
          </div>

          <div className="setup-group mb-8">
            <label className="block font-medium mb-2">Roadmap Duration (Days)</label>
            <select 
              value={roadmapDays} 
              onChange={e => setRoadmapDays(Number(e.target.value))}
            >
              <option value={5}>5 Days (Fast-Track)</option>
              <option value={10}>10 Days (Standard)</option>
              <option value={14}>14 Days (Comprehensive)</option>
              <option value={30}>30 Days (Expert Journey)</option>
            </select>
          </div>

          <button onClick={startTraining} className="primary-btn w-full py-4 text-lg">
            Start My Pipeline
          </button>
        </div>
      </div>
    );
  }

  if (loading && !trainingData) {
    return (
      <div className="training-loader">
        <Loader2 className="animate-spin" size={48} color="#6366f1" />
        <h2>Generating Your AI Career Roadmap...</h2>
        <p>Analyzing skills, crafting tailored questions, and building your {roadmapDays}-day plan.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="training-error">
        <AlertCircle size={48} color="#ef4444" />
        <h2>Oops! Something went wrong</h2>
        <p>{error}</p>
        <button onClick={() => fetchTrainingPlan()} className="retry-btn">Retry Generation</button>
      </div>
    );
  }

  if (!trainingData) return null;

  const skill_analysis = trainingData.skill_analysis || { 
    level: "Analyzing...", 
    missing_skills: [], 
    strengths: [], 
    focus_areas: [] 
  };
  const questions = Array.isArray(trainingData.questions) ? trainingData.questions : [];
  const tasks = Array.isArray(trainingData.tasks) ? trainingData.tasks : [];
  const roadmap = Array.isArray(trainingData.roadmap) ? trainingData.roadmap : [];

  return (
    <div className="training-dashboard-container">
      <header className="training-header">
        <div className="header-content">
          <div className="badge">AI Career Coach</div>
          <h1 className="training-main-title">Training & Interview Intelligence</h1>
          <p className="training-subtitle">Personalized preparation for your target job role</p>
        </div>
        <div className="header-stats">
          <div className="stat-card premium-stat">
            <div className="stat-icon-wrapper"><Trophy size={18} /></div>
            <span className="label">Points</span>
            <div className="value">
              <span className="pts-count">{sessionPoints}</span>
              <div 
                className="refresh-indicator" 
                title="Regenerate & Clear Cache"
                onClick={() => fetchTrainingPlan()}
              >
                <RefreshCw 
                  size={14} 
                  className={loading ? 'animate-spin' : ''} 
                />
              </div>
            </div>
          </div>
          <div className="stat-card premium-stat">
            <div className="stat-icon-wrapper"><Brain size={18} /></div>
            <span className="label">Readiness</span>
            <span className="value">{skill_analysis?.level || 'Intermediate'}</span>
          </div>
          <div className="stat-card premium-stat">
            <div className="stat-icon-wrapper"><Target size={18} /></div>
            <span className="label">Gap Skills</span>
            <span className="value">{skill_analysis?.missing_skills?.length || 0}</span>
          </div>
        </div>
      </header>

      <nav className="training-nav">
        <button 
          className={activeTab === 'analysis' ? 'active' : ''} 
          onClick={() => setActiveTab('analysis')}
        >
          <Brain size={18} /> Skill Analysis
        </button>
        <button 
          className={activeTab === 'interview' ? 'active' : ''} 
          onClick={() => setActiveTab('interview')}
        >
          <MessageSquare size={18} /> Interview Prep
        </button>
        <button 
          className={activeTab === 'task' ? 'active' : ''} 
          onClick={() => setActiveTab('task')}
        >
          <Layout size={18} /> Practical Tasks
        </button>
        <button 
          className={activeTab === 'roadmap' ? 'active' : ''} 
          onClick={() => setActiveTab('roadmap')}
        >
          <Calendar size={18} /> {roadmapDays}-Day Roadmap
        </button>
      </nav>

      <main className="training-content">
        {activeTab === 'analysis' && (
          <div className="analysis-view animate-fade-in">
            <div className="grid-2">
              <section className="card glass">
                <div className="card-header">
                  <Target color="#6366f1" />
                  <h3>Skill Gap Analysis</h3>
                </div>
                <div className="skill-list">
                  {skill_analysis.missing_skills.map((skill, i) => (
                    <div key={i} className="skill-item missing">
                      <AlertCircle size={14} /> {skill}
                    </div>
                  ))}
                </div>
              </section>

              <section className="card glass">
                <div className="card-header">
                  <Trophy color="#10b981" />
                  <h3>Your Strengths</h3>
                </div>
                <div className="skill-list">
                  {skill_analysis.strengths.map((skill, i) => (
                    <div key={i} className="skill-item strength">
                      <CheckCircle2 size={14} /> {skill}
                    </div>
                  ))}
                </div>
              </section>
            </div>

            <section className="card full-width glass mt-24">
              <div className="card-header">
                <Lightbulb color="#f59e0b" />
                <h3>Strategic Focus Areas</h3>
              </div>
              <div className="focus-grid">
                {skill_analysis.focus_areas.map((area, i) => (
                  <div key={i} className="focus-card">
                    <Zap size={20} />
                    <p>{area}</p>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}

        {activeTab === 'interview' && (() => {
          const topics = [...new Set(questions.map(q => q.cat || 'General'))];
          const actualTopic = selectedTopic === 'All' && topics.length > 0 ? topics[0] : selectedTopic;
          
          let currentTopicQuestions = topics.length > 0 ? questions.filter(q => (q.cat || 'General') === actualTopic) : questions;
          if (selectedQuizTypeFilter !== 'All') {
             currentTopicQuestions = currentTopicQuestions.filter(q => q.quiz_type === selectedQuizTypeFilter);
          }
          
          const currentQuestionIdx = selectedQuestion ? currentTopicQuestions.findIndex(q => q.id === selectedQuestion.id) : 0;
          const activeQuestion = currentTopicQuestions[currentQuestionIdx] || currentTopicQuestions[0] || selectedQuestion;

          return (
            <div className="interview-view animate-fade-in">
              <div className="interview-layout">
                <div className="questions-sidebar glass">
                  <div className="sidebar-title-wrapper">
                    <Brain color="#6366f1" size={20} />
                    <h3>Interview Topics</h3>
                  </div>
                  {topics.map((t, i) => (
                    <div key={i}>
                      <button 
                        className={`q-item ${actualTopic === t ? 'selected' : ''}`}
                        onClick={() => {
                            setSelectedTopic(t);
                            setSelectedQuizTypeFilter('All');
                            const topicQs = (trainingData.questions || []).filter(q => (q.cat || 'General') === t);
                            if (topicQs.length > 0) {
                              setSelectedQuestion(topicQs[0]);
                            } else {
                              setSelectedQuestion(null);
                              fetchTopicQuestions(t);
                            }
                            setAnswerInput('');
                            if (trainingData.answer_evaluation) {
                               setTrainingData(prev => ({...prev, answer_evaluation: null}));
                            }
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <p style={{ fontWeight: actualTopic === t ? 'bold' : 'normal', margin: 0 }}>{t}</p>
                          {Object.keys(topicAnswers).filter(id => {
                            const q = questions.find(q => q.id === id);
                            return q && (q.cat || 'General') === t;
                          }).length === questions.filter(q => (q.cat || 'General') === t).length && questions.filter(q => (q.cat || 'General') === t).length > 0 && (
                            <CheckCircle2 size={14} color="#10b981" />
                          )}
                        </div>
                      </button>
                    </div>
                  ))}
                  
                  <button 
                    className="reset-all-btn"
                    onClick={async () => {
                      const ok = await confirm("Reset all session progress?");
                      if (ok) { setTopicAnswers({}); setSessionPoints(0); }
                    }}
                    style={{ 
                      marginTop: '2rem', width: '100%', padding: '10px', borderRadius: '8px', 
                      background: 'rgba(239, 68, 68, 0.08)', color: '#ef4444', border: '1px solid rgba(239, 68, 68, 0.2)',
                      fontSize: '11px', fontWeight: 'bold', cursor: 'pointer'
                    }}
                  >
                    Reset Progress
                  </button>
                </div>

                <div className="answer-zone">
                  {activeQuestion && (
                    <div className="card glass relative">
                      <div className="question-filter-bar" style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginBottom: '2rem', padding: '6px', background: 'var(--bg-secondary)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                        {[
                          { id: 'All', label: 'All Questions' },
                          { id: 'mcq', label: 'MCQ' },
                          { id: 'fill_in_the_blank', label: 'Fill-in-the-Blank' },
                          { id: 'long_answer', label: 'Long Answer' }
                        ].map((filter) => (
                          <button 
                            key={filter.id}
                            style={{ 
                               padding: '8px 16px', fontSize: '13px', fontWeight: '600', borderRadius: '8px', cursor: 'pointer', transition: 'all 0.2s',
                               border: 'none',
                               background: selectedQuizTypeFilter === filter.id ? '#6366f1' : 'transparent', 
                               color: selectedQuizTypeFilter === filter.id ? '#ffffff' : '#64748b',
                               boxShadow: selectedQuizTypeFilter === filter.id ? '0 4px 6px -1px rgba(99, 102, 241, 0.2)' : 'none'
                             }}
                             onClick={() => {
                                setSelectedQuizTypeFilter(filter.id);
                                const qMatch = questions.find(q => (q.cat || 'General') === actualTopic && (filter.id === 'All' || q.quiz_type === filter.id));
                                if (qMatch) {
                                  setSelectedQuestion(qMatch);
                                  setAnswerInput(topicAnswers[qMatch.id]?.answer || '');
                                }
                             }}
                          >
                             {filter.label}
                          </button>
                        ))}
                      </div>
                      
                      <div className="active-question-card">
                        <div className="question-meta-row">
                           <span className="badge quiz-type-badge">{activeQuestion.quiz_type?.replace(/_/g, ' ').toUpperCase()}</span>
                           <span className="question-counter">Question {currentQuestionIdx + 1} of {currentTopicQuestions.length}</span>
                        </div>
                        <h4 className="active-question-text">{activeQuestion.question}</h4>
                        <div className="question-icon-center">
                          <Cpu size={40} opacity={0.1} />
                        </div>
                      </div>
                      
                      <div className="input-field-container" style={{ minHeight: '200px' }}>
                        {topicLoadingMap[actualTopic] ? (
                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '200px', gap: '1rem' }}>
                                <Loader2 className="animate-spin" size={32} color="#6366f1" />
                                <p style={{ color: '#64748b', fontWeight: '500' }}>Fetching expert questions for {actualTopic}...</p>
                            </div>
                        ) : activeQuestion?.quiz_type === 'mcq' ? (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '1.5rem', width: '100%' }}>
                            {activeQuestion.options?.map((opt, i) => (
                              <label key={i} style={{ 
                                  display: 'flex', alignItems: 'center', width: '100%', padding: '1.25rem', 
                                  borderRadius: '12px', cursor: topicAnswers[activeQuestion.id] ? 'default' : 'pointer', 
                                  border: answerInput === opt ? '2px solid var(--accent)' : '1px solid var(--border-color)', 
                                  background: answerInput === opt ? 'rgba(99, 102, 241, 0.05)' : 'var(--bg-card)',
                                  transition: 'all 0.2s',
                                  opacity: topicAnswers[activeQuestion.id] && answerInput !== opt ? 0.6 : 1
                               }}>
                                <input 
                                  type="radio" 
                                  name="mcq" 
                                  value={opt} 
                                  disabled={!!topicAnswers[activeQuestion.id]}
                                  checked={answerInput === opt} 
                                  onChange={(e) => setAnswerInput(e.target.value)} 
                                  style={{ width: '1.2rem', height: '1.2rem', flexShrink: 0, marginRight: '1rem', accentColor: 'var(--accent)' }}
                                />
                                <span style={{ display: 'block', flex: 1, fontSize: '1.1rem', color: 'var(--text-primary)', fontWeight: answerInput === opt ? '600' : '500' }}>{opt}</span>
                              </label>
                            ))}
                          </div>
                        ) : (
                          <div className="text-input-wrapper">
                            {activeQuestion?.quiz_type === 'fill_in_the_blank' ? (
                              <input 
                                type="text"
                                placeholder="Type your answer here..."
                                value={answerInput}
                                disabled={!!topicAnswers[activeQuestion.id]}
                                onChange={(e) => setAnswerInput(e.target.value)}
                                style={{ 
                                  width: '100%', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-color)',
                                  fontSize: '1.1rem', outline: 'none', transition: 'border-color 0.2s',
                                  backgroundColor: topicAnswers[activeQuestion.id] ? 'var(--bg-secondary)' : 'var(--bg-card)'
                                }}
                              />
                            ) : (
                              <textarea 
                                placeholder="Provide a detailed professional response..."
                                value={answerInput}
                                disabled={!!topicAnswers[activeQuestion.id]}
                                onChange={(e) => setAnswerInput(e.target.value)}
                                rows={6}
                                style={{ 
                                  width: '100%', padding: '1.25rem', borderRadius: '12px', border: '1px solid var(--border-color)',
                                  fontSize: '1.1rem', outline: 'none', transition: 'border-color 0.2s', resize: 'vertical',
                                  backgroundColor: topicAnswers[activeQuestion.id] ? 'var(--bg-secondary)' : 'var(--bg-card)'
                                }}
                              />
                            )}
                          </div>
                        )}
                      </div>

                      <div className="action-button-group">
                          <button 
                            className="secondary-btn"
                            onClick={() => {
                              setAnswerInput('');
                              if (topicAnswers[activeQuestion.id]) {
                                const newAnswers = { ...topicAnswers };
                                const wasCorrect = newAnswers[activeQuestion.id].correct;
                                delete newAnswers[activeQuestion.id];
                                setTopicAnswers(newAnswers);
                                if (wasCorrect) setSessionPoints(p => Math.max(0, p - 2));
                              }
                            }}
                            style={{ padding: '12px', borderRadius: '10px', background: 'var(--bg-secondary)', color: 'var(--text-secondary)', fontWeight: '700', border: 'none', cursor: 'pointer' }}
                          >
                            Reset
                          </button>

                          {!topicAnswers[activeQuestion.id] ? (
                            <button 
                              className="primary-btn"
                              disabled={!answerInput.trim()}
                              onClick={() => {
                                if (!answerInput.trim()) return;
                                const isMcq = activeQuestion.quiz_type === 'mcq';
                                let isCorrect = true;
                                if (activeQuestion.correct_answer) {
                                    if (isMcq) isCorrect = answerInput === activeQuestion.correct_answer;
                                    else isCorrect = (answerInput || '').toLowerCase().includes((activeQuestion.correct_answer || '').toLowerCase());
                                }
                                setTopicAnswers(prev => ({
                                    ...prev,
                                    [activeQuestion.id]: { answer: answerInput, correct: isCorrect, explanation: activeQuestion.explanation }
                                }));
                                if (isCorrect) setSessionPoints(prev => prev + 2);
                              }}
                              style={{ padding: '12px', borderRadius: '10px', background: '#6366f1', color: 'white', fontWeight: '700', border: 'none', cursor: !answerInput.trim() ? 'not-allowed' : 'pointer', opacity: !answerInput.trim() ? 0.6 : 1 }}
                            >
                              Evaluate Answer
                            </button>
                          ) : (
                            <button 
                              disabled 
                              style={{ 
                                 padding: '12px', 
                                 borderRadius: '10px', 
                                 background: topicAnswers[activeQuestion.id].correct ? '#10b981' : '#ef4444', 
                                 color: 'white', 
                                 fontWeight: '700', 
                                 border: 'none', 
                                 cursor: 'default' 
                              }}
                            >
                              {topicAnswers[activeQuestion.id].correct ? 'Correct ✓' : 'Wrong ✗'}
                            </button>
                          )}

                          <button 
                            className="secondary-btn"
                            disabled={!!topicAnswers[activeQuestion.id]}
                            onClick={() => {
                               setTopicAnswers(prev => ({
                                  ...prev,
                                  [activeQuestion.id]: { answer: "Skipped", correct: false, explanation: "You skipped this question." }
                               }));
                               if (currentQuestionIdx < currentTopicQuestions.length - 1) {
                                  setSelectedQuestion(currentTopicQuestions[currentQuestionIdx + 1]);
                                  setAnswerInput(topicAnswers[currentTopicQuestions[currentQuestionIdx + 1].id]?.answer || '');
                               }
                            }}
                            style={{ padding: '12px', borderRadius: '10px', background: 'var(--bg-hover)', color: 'var(--text-muted)', fontWeight: '700', border: 'none', cursor: topicAnswers[activeQuestion.id] ? 'not-allowed' : 'pointer', opacity: topicAnswers[activeQuestion.id] ? 0.5 : 1 }}
                          >
                            Skip
                          </button>
                      </div>

                      <div className="navigation-buttons" style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1.5rem' }}>
                        <button 
                          disabled={currentQuestionIdx <= 0}
                          onClick={() => {
                            const prevQ = currentTopicQuestions[currentQuestionIdx - 1];
                            setSelectedQuestion(prevQ);
                            setAnswerInput(topicAnswers[prevQ.id]?.answer || '');
                          }}
                          style={{ background: 'none', border: 'none', color: '#6366f1', fontWeight: '600', cursor: currentQuestionIdx <= 0 ? 'default' : 'pointer', opacity: currentQuestionIdx <= 0 ? 0.4 : 1, display: 'flex', alignItems: 'center', gap: '4px' }}
                        >
                          <ChevronRight style={{ transform: 'rotate(180deg)' }} size={16} /> Previous
                        </button>
                        <button 
                          disabled={currentQuestionIdx >= currentTopicQuestions.length - 1}
                          onClick={() => {
                            const nextQ = currentTopicQuestions[currentQuestionIdx + 1];
                            setSelectedQuestion(nextQ);
                            setAnswerInput(topicAnswers[nextQ.id]?.answer || '');
                          }}
                          style={{ background: 'none', border: 'none', color: '#6366f1', fontWeight: '600', cursor: currentQuestionIdx >= currentTopicQuestions.length - 1 ? 'default' : 'pointer', opacity: currentQuestionIdx >= currentTopicQuestions.length - 1 ? 0.4 : 1, display: 'flex', alignItems: 'center', gap: '4px' }}
                        >
                          Next <ChevronRight size={16} />
                        </button>
                      </div>

                      {topicAnswers[activeQuestion.id] && (
                        <div className={`evaluation-result animate-slide-up mt-8 border-l-4 ${topicAnswers[activeQuestion.id].correct ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'} p-6 rounded-r-xl`}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                            {topicAnswers[activeQuestion.id].correct ? <CheckCircle2 size={24} color="#10b981" /> : <AlertCircle size={24} color="#ef4444" />}
                            <h5 style={{ margin: 0, fontSize: '1.1rem', fontWeight: '700', color: topicAnswers[activeQuestion.id].correct ? '#166534' : '#991b1b' }}>
                               {topicAnswers[activeQuestion.id].correct ? 'Spot On!' : 'Room for Improvement'}
                            </h5>
                          </div>
                          <div className="eval-text" style={{ fontSize: '0.95rem', color: '#475569', lineHeight: '1.6' }}>
                             {activeQuestion.correct_answer && <p style={{ marginBottom: '8px' }}><span style={{ fontWeight: '700', color: '#10b981' }}>Correct Answer:</span> {activeQuestion.correct_answer}</p>}
                             <p><span style={{ fontWeight: '700', color: 'var(--text-primary)' }}>Expert Insights:</span> {topicAnswers[activeQuestion.id].explanation || "Great job covering this concept!"}</p>
                          </div>
                        </div>
                      )}
                      
                      {Object.keys(topicAnswers).filter(id => questions.find(q => q.id === id && (q.cat || 'General') === actualTopic)).length === currentTopicQuestions.length && currentTopicQuestions.length > 0 && (
                         <div className="summary-card-premium mt-12 p-8 rounded-2xl animate-slide-up" style={{ background: 'linear-gradient(135deg, #6366f1, #a855f7)', color: 'white', position: 'relative', overflow: 'hidden' }}>
                            <div style={{ position: 'absolute', top: '-20px', right: '-20px', opacity: 0.1 }}>
                              <Brain size={120} />
                            </div>
                            <h3 style={{ fontSize: '1.5rem', fontWeight: '800', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                              <Trophy size={28} /> Topic Mastery: {actualTopic}
                            </h3>
                            <p style={{ opacity: 0.9, fontSize: '1.1rem', marginBottom: '2rem', maxWidth: '80%' }}>
                              You've completed all {currentTopicQuestions.length} questions for this module.
                            </p>
                            <button 
                              onClick={() => {
                                const nextIdx = topics.indexOf(actualTopic) + 1;
                                if (nextIdx < topics.length) {
                                  setSelectedTopic(topics[nextIdx]);
                                  setSelectedQuizTypeFilter('All');
                                  const firstQ = questions.find(q => (q.cat || 'General') === topics[nextIdx]);
                                  setSelectedQuestion(firstQ);
                                  setAnswerInput('');
                                } else {
                                  setActiveTab('task');
                                }
                              }}
                              style={{ 
                                padding: '12px 32px', borderRadius: '100px', 
                                background: 'white', color: '#6366f1', border: 'none', 
                                fontWeight: '800', fontSize: '1rem', cursor: 'pointer',
                                boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)'
                              }}
                            >
                              {topics.indexOf(actualTopic) < topics.length - 1 ? 'Go to Next Topic' : 'Proceed to Practical Tasks'}
                            </button>
                         </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })()}

        {activeTab === 'task' && (
          <div className="task-view animate-fade-in">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">Targeted Practical Tasks</h2>
              <span className="badge opacity-80">{tasks?.length || 0} Assignments</span>
            </div>
            
            <div className="task-list" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {tasks?.map((taskItem, index) => (
                <div key={index} className="card glass task-card">
                  <div className="task-header">
                    <span className={`difficulty ${(taskItem.difficulty || '').toLowerCase()}`}>{taskItem.difficulty || 'Mixed'}</span>
                    <h2>{taskItem.title}</h2>
                  </div>
                  <p className="description">{taskItem.description}</p>
                  
                  <div className="task-grid mt-4 grid md:grid-cols-2 gap-6">
                    <div className="section">
                      <h4><Target size={16} className="inline mr-2" /> Key Requirements</h4>
                      <ul className="list-disc pl-5 opacity-80 space-y-1">
                        {taskItem.requirements?.map((r, i) => <li key={i}>{r}</li>)}
                      </ul>
                    </div>
                    <div className="section">
                      <h4><Cpu size={16} className="inline mr-2" /> Expected Output</h4>
                      <p className="opacity-80">{taskItem.expected_output}</p>
                    </div>
                  </div>

                  <div className="task-footer mt-6 pt-4 border-t border-white/10 flex justify-between items-start">
                    <p className="text-sm opacity-60" style={{ maxWidth: '70%' }}>Complete this assignment to showcase your {taskItem.difficulty} mastery.</p>
                    <div className="task-actions-stack horizontal">
                       <button 
                         className="task-btn primary"
                         style={{ 
                            background: tasksStarted.includes(index) ? '#4f46e5' : '#6366f1',
                            opacity: tasksCompleted.includes(index) ? 0.5 : 1,
                            cursor: tasksCompleted.includes(index) ? 'not-allowed' : 'pointer'
                         }}
                         onClick={() => {
                            if (!tasksStarted.includes(index) && !tasksCompleted.includes(index)) {
                               setTasksStarted([...tasksStarted, index]);
                            }
                         }}
                       >
                         {tasksStarted.includes(index) ? 'Project Active' : 'Start Project'}
                       </button>
                       <button 
                         className={`task-btn success ${tasksCompleted.includes(index) ? 'success-animation' : ''}`}
                         style={{ 
                            background: tasksCompleted.includes(index) ? '#10b981' : 'rgba(16, 185, 129, 0.1)',
                            color: tasksCompleted.includes(index) ? 'white' : '#10b981',
                            border: tasksCompleted.includes(index) ? 'none' : '1px solid #10b981',
                            cursor: tasksCompleted.includes(index) ? 'default' : 'pointer'
                         }}
                         onClick={() => {
                           if (!tasksCompleted.includes(index)) {
                             setTasksCompleted([...tasksCompleted, index]);
                             setSessionPoints(prev => prev + 50);
                           }
                         }}
                       >
                         {tasksCompleted.includes(index) ? 'Completed ✓' : 'Mark Completed'}
                       </button> 
                    </div>
                  </div>
                </div>
              ))}
              
              {(!tasks || tasks.length === 0) && (
                <div className="p-8 text-center glass rounded-lg">
                  <p>No practical tasks generated for this skill gap.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'roadmap' && (
          <div className="roadmap-view animate-fade-in">
            <h2 className="text-xl font-bold mb-6">Your Personalized {roadmapDays}-Day Roadmap</h2>
            <div className="roadmap-timeline">
              {roadmap?.map((day, i) => (
                <div key={i} className="roadmap-item">
                  <div className="day-circle">Day {day.day}</div>
                  <div className="roadmap-card glass roadmap-flex-item">
                    <div className="roadmap-content" style={{ flex: 1 }}>
                        <div className="mb-2 pb-2 border-b border-white/5">
                           {day.focus ? (
                               <h4 className="text-blue-500 font-bold uppercase text-sm tracking-wide m-0" style={{ fontSize: '1rem' }}>Day {day.day}: {day.focus}</h4>
                           ) : (
                               <h4 className="text-blue-500 font-bold uppercase text-sm tracking-wide m-0" style={{ fontSize: '1rem' }}>Day {day.day}: Core Concept Focus</h4>
                           )}
                        </div>
                        {roadmapExpanded.includes(i) && (
                             <div className="text-sm opacity-80 mb-3 bg-black/30 p-4 rounded-xl border border-white/5 animate-slide-up">
                                 <strong>Learning Focus:</strong> Deep dive into {day.focus || 'modern tech stacks'}. This day covers key patterns, common pitfalls, and architectural insights specific to this skill gap.
                             </div>
                        )}
                        <p className="text-white opacity-90 m-0" style={{ fontSize: '0.95rem', lineHeight: '1.6' }}>{day.task}</p>
                    </div>

                    <div className="roadmap-actions right-side">
                         <button className="roadmap-btn-curved secondary" 
                           onClick={() => setRoadmapExpanded(prev => prev.includes(i) ? prev.filter(x => x !== i) : [...prev, i])}>
                            {roadmapExpanded.includes(i) ? 'Hide' : 'Details'}
                         </button>
                         <button className="roadmap-btn-curved success" 
                           style={{ 
                               borderColor: roadmapCompleted.includes(i) ? '#10b981' : 'rgba(16, 185, 129, 0.5)',
                               backgroundColor: roadmapCompleted.includes(i) ? '#10b981' : 'rgba(16, 185, 129, 0.1)',
                               color: roadmapCompleted.includes(i) ? '#ffffff' : '#34d399'
                           }}
                           onClick={() => {
                             if (!roadmapCompleted.includes(i)) {
                                setRoadmapCompleted([...roadmapCompleted, i]);
                                setSessionPoints(p => p + 20);
                             }
                         }}>
                            {roadmapCompleted.includes(i) ? 'Done ✓' : 'Finish'}
                         </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default TrainingDashboard;
