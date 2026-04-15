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
  RefreshCw,
  TrendingUp,
  History,
  CheckCircle
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
  const [chatTurn, setChatTurn] = useState(0);
  const [chatHistory, setChatHistory] = useState([]);
  
  useEffect(() => {
    if (hasStarted && chatHistory.length === 0 && !loading) {
      fetchTrainingPlan();
    }
  }, [hasStarted, chatHistory, loading]);

  const startTraining = () => {
    setHasStarted(true);
    fetchTrainingPlan();
  };

  const fetchTrainingPlan = async (question = null, answer = null) => {
    try {
      if (!answer) setLoading(true);
      setError(null);
      
      const params = { 
        match_id: matchId, 
        roadmap_days: roadmapDays, 
        quiz_type: quizType,
        chat_turn: chatTurn,
        _t: Date.now() 
      };
      
      if (question) params.question = question;
      if (answer) params.answer = answer;

      const response = await api.post('/training/generate', null, { params });
      const freshData = response.data || {};
      
      // Update data
      setTrainingData(freshData);
      
      // Handle conversational flow (Single Append)
      if (answer) {
        setChatHistory(prev => [
          ...prev, 
          { role: 'user', text: answer },
          { 
             role: 'coach', 
             text: freshData.coach_comment || "Analysis processed.", 
             next: freshData.next_question || null 
          }
        ]);
        setChatTurn(prev => prev + 1);
      } else {
        // Initial Startup
        setChatHistory([
           { 
              role: 'coach', 
              text: freshData.coach_comment || "Initializing strategic environment...", 
              next: freshData.next_question || null 
           }
        ]);
      }
      
      if (freshData.next_question) {
        setSelectedQuestion({ 
          question: freshData.next_question, 
          quiz_type: 'long_answer' 
        });
      }

      if (answer && freshData.answer_evaluation?.score) {
          setSessionPoints(prev => prev + freshData.answer_evaluation.score);
      }
    } catch (err) {
      console.error('CRITICAL: Training Plan Fetch Error:', err);
      setError(err.response?.data?.detail || 'The AI is currently processing many requests. Please try clicking "Start My Pipeline" again or refresh.');
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluateAnswer = async () => {
    if (!answerInput.trim()) return;
    setEvaluating(true);
    const currentQ = selectedQuestion?.question;
    const currentAns = answerInput;
    setAnswerInput('');
    await fetchTrainingPlan(currentQ, currentAns);
    setEvaluating(false);
  };

  if (!hasStarted) {
    return (
      <div className="training-setup-container animate-fade-in">
        <div className="setup-wrapper">
          <div className="setup-hero-text">
            <h1 className="premium-gradient-text">Career Intelligence Engine</h1>
            <p className="subtitle">Adaptive. Data-Driven. Strategic.</p>
          </div>
          
          <div className="setup-grid">
            <div className="card glass premium-border setup-card">
              <div className="card-header pb-4 mb-6">
                <Zap color="#6366f1" size={24} />
                <h2 className="text-xl font-bold">Configure Your Experience</h2>
              </div>
              
              <div className="setup-group mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <MessageSquare size={16} color="#6366f1" />
                  <label className="font-bold text-sm uppercase tracking-wider opacity-80">Interview Pattern</label>
                </div>
                <select 
                  value={quizType} 
                  onChange={e => setQuizType(e.target.value)}
                  className="premium-select"
                >
                  <option value="Mixed">Mixed (Human-Like Inquiry)</option>
                  <option value="MCQ">Technical MCQ Focus</option>
                  <option value="Fill-in-the-Blank">Concept Validation</option>
                  <option value="Long Answer">Deep Technical Analysis</option>
                </select>
              </div>

              <div className="setup-group mb-8">
                <div className="flex items-center gap-2 mb-3">
                  <Calendar size={16} color="#10b981" />
                  <label className="font-bold text-sm uppercase tracking-wider opacity-80">Evolution Roadmap</label>
                </div>
                <select 
                  value={roadmapDays} 
                  onChange={e => setRoadmapDays(Number(e.target.value))}
                  className="premium-select"
                >
                  <option value={5}>5 Days (Intensive Sprint)</option>
                  <option value={10}>10 Days (Balanced Growth)</option>
                  <option value={14}>14 Days (Expert Transition)</option>
                  <option value={30}>30 Days (Mastery Journey)</option>
                </select>
              </div>

              <button onClick={startTraining} className="primary-btn w-full py-4 text-lg font-bold glow-on-hover">
                Initialize Carrier AI
              </button>
            </div>

            <div className="setup-info-panel">
               <div className="info-feature">
                  <div className="feature-icon"><Brain size={20} /></div>
                  <div className="feature-text">
                     <h4>Adaptive Questioning</h4>
                     <p>Our engine adapts to your previous answers, digging deeper into your strengths and identifying hidden gaps.</p>
                  </div>
               </div>
               <div className="info-feature">
                  <div className="feature-icon"><Target size={20} /></div>
                  <div className="feature-text">
                     <h4>Job-Centric DNA</h4>
                     <p>Content is dynamically generated based on your target job description and current resume profile.</p>
                  </div>
               </div>
               <div className="info-feature">
                  <div className="feature-icon"><Cpu size={20} /></div>
                  <div className="feature-text">
                     <h4>Skill Analysis Engine</h4>
                     <p>Receive a structured confidence profile across key technologies once the session is finalized.</p>
                  </div>
               </div>
               
               <div className="setup-trust-footer mt-8 pt-6 border-t border-white/5">
                  <div className="flex items-center gap-2 opacity-60 italic text-sm">
                     <FileText size={14} />
                     <span>Processing: {matchId.substring(0,8)}... Matching Logic Active</span>
                  </div>
               </div>
            </div>
          </div>
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
  const job_role = trainingData.job_role || "Target Role";

  return (
    <div className="training-dashboard-container">
      <header className="training-header">
        <div className="header-content">
          <div className="badge">AI Career Coach</div>
          <h1 className="training-main-title">Training & Interview Intelligence</h1>
          <p className="training-subtitle">Personalized preparation for your target job role</p>
        </div>

        <div className="header-coach-insight animate-fade-in">
          <div className="coach-status-box" style={{ background: 'var(--bg-card)', padding: '16px 32px', borderRadius: '24px', border: '1px solid var(--border-color)', boxShadow: 'var(--glass-shadow)', display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div className="coach-icon" style={{ width: '48px', height: '48px', background: 'var(--grad-primary)', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px', boxShadow: '0 4px 12px rgba(99,102,241,0.2)' }}>🤖</div>
            <div>
              <p style={{ margin: 0, fontSize: '11px', fontWeight: 800, color: '#6366f1', textTransform: 'uppercase', letterSpacing: '1px' }}>System Status</p>
              <p style={{ margin: 0, fontSize: '15px', color: 'var(--text-primary)', fontWeight: 600 }}>
                {sessionPoints > 50 ? "Strategic Profile Active" : 
                 sessionPoints > 20 ? "Synchronizing DNA..." : 
                 "Initializing Career Logic"}
              </p>
            </div>
          </div>
        </div>

        <div className="header-stats">
          <div className="stat-card premium-stat premium-border">
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
          <div className="stat-card premium-stat premium-border">
            <div className="stat-icon-wrapper"><Brain size={18} /></div>
            <span className="label">Readiness</span>
            <span className="value">{skill_analysis?.level || 'Intermediate'}</span>
          </div>
          <div className="stat-card premium-stat premium-border">
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
             {!trainingData.is_profile_complete ? (
                <div className="preliminary-analysis-header glass p-8 rounded-3xl border border-indigo-500/20 mb-8 bg-indigo-500/5">
                   <div className="flex items-center gap-4 mb-4">
                      <div className="status-orb pulse-blue"></div>
                      <h3 className="m-0 text-indigo-400 uppercase tracking-widest text-sm font-bold">Intelligence Engine Active</h3>
                   </div>
                   <h2 className="text-2xl font-bold mb-2">Analyzing Your Career Strategy</h2>
                   <p className="opacity-70 m-0 max-w-2xl">
                      CAREER AI is currently cross-referencing your experience with the market standards for a {job_role}. 
                      The Decision Engine will provide your roadmap and job matches below.
                   </p>
                </div>
             ) : (
              <>
                {trainingData.career_insight && (
                  <section className="card full-width glass premium-border mb-8 highlight-purple-glow">
                    <div className="card-header">
                       <TrendingUp color="#a78bfa" />
                       <h3>Strategic Career Insight</h3>
                    </div>
                    <p style={{ fontSize: '1.2rem', lineHeight: '1.8', color: 'var(--text-primary)', fontWeight: '500' }}>
                      {trainingData.career_insight}
                    </p>
                  </section>
                )}

                <div className="grid-2">
                  <section className="card glass premium-border">
                    <div className="card-header">
                      <Cpu color="#6366f1" />
                      <h3>Skill DNA Profile</h3>
                    </div>
                    <div className="skill-dna-list" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      {trainingData.skill_profile?.map((item, i) => (
                        <div key={i} className="skill-dna-item">
                           <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                              <span className="skill-name font-bold">{item.skill}</span>
                              <span className="skill-pct font-bold" style={{ color: '#6366f1' }}>{item.confidence}</span>
                           </div>
                           <div className="dna-bar-bg" style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', overflow: 'hidden' }}>
                              <div className="dna-bar-fill" style={{ height: '100%', width: item.confidence, background: 'var(--grad-primary)', borderRadius: '4px' }}></div>
                           </div>
                        </div>
                      ))}
                    </div>
                  </section>

                  <section className="card glass premium-border">
                    <div className="card-header">
                      <Target color="#10b981" />
                      <h3>Top Match Intelligence</h3>
                    </div>
                    <div className="match-dna-list" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      {trainingData.top_job_matches?.map((match, i) => (
                        <div key={i} className="match-dna-card p-4 rounded-xl" style={{ border: '1px solid var(--border-color)', background: 'rgba(255,255,255,0.02)' }}>
                           <div className="flex justify-between items-start mb-2">
                              <h4 className="m-0 font-bold" style={{ fontSize: '1.1rem' }}>{match.role}</h4>
                              <span className="badge match-badge" style={{ background: '#10b981', color: 'white' }}>{match.match_score}</span>
                           </div>
                           <p className="text-sm opacity-70 m-0">{match.why}</p>
                        </div>
                      ))}
                    </div>
                  </section>
                </div>
              </>
            )}

            <div className="grid-2 mt-8">
               <section className="card glass premium-border highlight-amber-glow">
                  <div className="card-header bulletin-header">
                     <AlertCircle color="#f59e0b" />
                     <h3>Targeted Skill Gaps Bulletin</h3>
                  </div>
                  <div className="bulletin-content">
                     {skill_analysis.missing_skills?.map((skill, i) => (
                     <div key={i} className="bulletin-item missing animate-slide-right" style={{ animationDelay: `${i * 0.1}s` }}>
                        <div className="bullet-indicator"></div>
                        <div className="item-text">
                           <span className="skill-title">{skill}</span>
                           <span className="item-meta">Priority Growth Area</span>
                        </div>
                     </div>
                     ))}
                     {(!skill_analysis.missing_skills || skill_analysis.missing_skills.length === 0) && (
                        <p className="text-sm opacity-50 p-4 italic">Awaiting technical synchronization...</p>
                     )}
                  </div>
               </section>

               <section className="card glass premium-border highlight-emerald-glow">
                  <div className="card-header bulletin-header">
                     <Trophy color="#10b981" />
                     <h3>Verified Core Strengths</h3>
                  </div>
                  <div className="bulletin-content">
                     {skill_analysis.strengths?.map((skill, i) => (
                     <div key={i} className="bulletin-item strength animate-slide-left" style={{ animationDelay: `${i * 0.1}s` }}>
                        <div className="bullet-indicator success"></div>
                        <div className="item-text">
                           <span className="skill-title">{skill}</span>
                           <span className="item-meta">Validated Proficiency</span>
                        </div>
                     </div>
                     ))}
                     {(!skill_analysis.strengths || skill_analysis.strengths.length === 0) && (
                        <p className="text-sm opacity-50 p-4 italic">Awaiting technical verification...</p>
                     )}
                  </div>
                </section>
             </div>
          </div>
        )}

        {activeTab === 'interview' && (
          <div className="interview-view animate-fade-in chat-mode">
             <div className="chat-container glass premium-border">
                <div className="chat-header">
                   <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div className="coach-avatar">🤖</div>
                      <div>
                        <h3 className="m-0">CAREER AI Coach</h3>
                        <p className="m-0 text-xs opacity-60">Intelligence Decision Engine</p>
                      </div>
                   </div>
                   <div className="progress-pills" style={{ display: 'flex', gap: '4px' }}>
                      {[...Array(5)].map((_, i) => (
                        <div key={i} className={`pill ${chatTurn > i ? 'complete' : chatTurn === i ? 'active' : ''}`} />
                      ))}
                   </div>
                </div>

                <div className="chat-messages" id="chat-scroller">
                   {chatHistory.map((msg, i) => (
                      <div key={i} className={`chat-message ${msg.role} animate-slide-up`}>
                         {msg.role === 'coach' && <div className="bubble-avatar assistant-avatar">🤖</div>}
                         <div className="message-bubble">
                            {msg.text}
                            {msg.next && (
                               <div className="msg-question">
                                  <strong>Next Inquiry:</strong><br />
                                  {msg.next}
                               </div>
                            )}
                         </div>
                         {msg.role === 'user' && <div className="bubble-avatar user-avatar">👤</div>}
                      </div>
                   ))}
                   {evaluating && (
                      <div className="chat-message coach">
                        <div className="message-bubble typing">
                           <Loader2 className="animate-spin inline mr-2" size={14} /> 
                           Analyzing response...
                        </div>
                      </div>
                   )}
                   <div ref={el => { if(el) el.scrollIntoView({ behavior: 'smooth' }) }}></div>
                </div>

                <div className="chat-input-zone">
                     <textarea 
                       placeholder="Provide your professional insight..."
                       value={answerInput}
                       onChange={(e) => setAnswerInput(e.target.value)}
                       onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                             e.preventDefault();
                             handleEvaluateAnswer();
                          }
                       }}
                       rows={1}
                     />
                     <button onClick={handleEvaluateAnswer} disabled={!answerInput.trim() || evaluating} className="send-btn">
                        <ChevronRight />
                     </button>
                  </div>
             </div>
          </div>
        )}

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
            {!trainingData.is_profile_complete ? (
               <div className="card glass premium-border text-center p-12">
                  <div className="lock-icon mb-6">
                    <Calendar className="mx-auto" size={48} color="#6366f1" />
                  </div>
                  <h3>Dynamic Roadmap is Locked</h3>
                  <p className="opacity-60 max-w-md mx-auto">
                    Complete your interview session with CAREER AI to unlock a detailed daily plan 
                    tailored to your identified skill gaps.
                  </p>
                  <button onClick={() => setActiveTab('interview')} className="primary-btn mt-6">
                    Launch AI Chat
                  </button>
               </div>
            ) : (
              <>
                <h2 className="text-xl font-bold mb-6">Your Personalized {roadmapDays}-Day Roadmap</h2>
                <div className="roadmap-timeline">
                  {roadmap?.map((day, i) => (
                    <div key={i} className="roadmap-item">
                      <div className="day-circle">{String(day.day).toLowerCase().includes('day') ? day.day : `Day ${day.day}`}</div>
                      <div className="roadmap-card glass roadmap-flex-item">
                        <div className="roadmap-content" style={{ flex: 1 }}>
                            <div className="mb-2 pb-2 border-b border-white/5">
                               {day.focus ? (
                                   <h4 className="text-blue-500 font-bold uppercase text-sm tracking-wide m-0" style={{ fontSize: '1rem' }}>{String(day.day).toLowerCase().includes('day') ? day.day : `Day ${day.day}`}: {day.focus}</h4>
                               ) : (
                                   <h4 className="text-blue-500 font-bold uppercase text-sm tracking-wide m-0" style={{ fontSize: '1rem' }}>{String(day.day).toLowerCase().includes('day') ? day.day : `Day ${day.day}`}: Core Concept Focus</h4>
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
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default TrainingDashboard;
