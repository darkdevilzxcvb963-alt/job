import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from 'react-query'
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, LineChart, Line, AreaChart, Area 
} from 'recharts'
import { TrendingUp, Users, Briefcase, Target, PieChart as PieIcon, BarChart2 } from 'lucide-react'
import { getSkillDemand, getMatchQualityStats, getRecruitmentFunnel } from '../services/api'
import '../styles/Analytics.css'

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

const AnalyticsDashboard = () => {
  const { data: skillDemand, isLoading: loadingSkills } = useQuery('skillDemand', () => getSkillDemand().then(r => r.data))
  const { data: matchQuality, isLoading: loadingQuality } = useQuery('matchQuality', () => getMatchQualityStats().then(r => r.data))
  const { data: funnelData, isLoading: loadingFunnel } = useQuery('recruitmentFunnel', () => getRecruitmentFunnel().then(r => r.data))
  
  const navigate = useNavigate()

  if (loadingSkills || loadingQuality || loadingFunnel) {
    return (
      <div className="analytics-loading">
        <div className="premium-loader"></div>
        <p>Crunching intelligence data...</p>
      </div>
    )
  }

  const funnelChartData = [
    { name: 'Candidates', value: funnelData?.funnel?.total_candidates || 0 },
    { name: 'Matches', value: funnelData?.funnel?.total_matches_generated || 0 },
    { name: 'Applied', value: funnelData?.funnel?.applied || 0 },
    { name: 'Screened', value: funnelData?.funnel?.screened || 0 },
    { name: 'Interview', value: funnelData?.funnel?.interview || 0 },
    { name: 'Offered', value: funnelData?.funnel?.offered || 0 },
    { name: 'Hired', value: (funnelData?.funnel?.hired || 0) },
  ]

  const distributionData = [
    { name: 'Excellent (80%+)', value: matchQuality?.score_distribution?.excellent_80_plus || 0 },
    { name: 'Good (60-80%)', value: matchQuality?.score_distribution?.good_60_80 || 0 },
    { name: 'Fair (40-60%)', value: matchQuality?.score_distribution?.fair_40_60 || 0 },
    { name: 'Low (<40%)', value: matchQuality?.score_distribution?.low_under_40 || 0 },
  ]

  const distributionBarData = [
    { range: '80-100%', count: matchQuality?.score_distribution?.excellent_80_plus || 0, color: '#10b981', min: 0.8, max: 1.0 },
    { range: '60-80%', count: matchQuality?.score_distribution?.good_60_80 || 0, color: '#f59e0b', min: 0.6, max: 0.8 },
    { range: '40-60%', count: matchQuality?.score_distribution?.fair_40_60 || 0, color: '#f97316', min: 0.4, max: 0.6 },
    { range: '<40%', count: matchQuality?.score_distribution?.low_under_40 || 0, color: '#ef4444', min: 0.0, max: 0.4 },
  ]

  const generateInsight = () => {
    if (!matchQuality) return null;
    const dist = matchQuality.score_distribution;
    const total = Object.values(dist).reduce((a, b) => a + b, 0);
    
    // If we are showing platform stats as fallback
    const isPlatform = matchQuality.total_platform_matches > 0 && total === matchQuality.total_platform_matches;

    if (total === 0) return "Global Talent Pool: No candidate data available in the system yet.";
    
    if (isPlatform) {
      return "Viewing platform-wide talent distribution. Get started by posting a job to see your specific candidate matches!";
    }

    const highMatchPerc = (dist.excellent_80_plus / total) * 100;
    if (highMatchPerc < 10) {
      return `Market Insight: Only ${highMatchPerc.toFixed(0)}% of matches are high quality. Consider optimizing your job descriptions.`;
    }
    return "Talent pool intelligence: Your active roles are attracting high-quality talent. Focus on excellent matches.";
  }

  return (
    <div className="analytics-dashboard page-container">
      <header className="analytics-header">
        <div className="header-icon-box">
          <TrendingUp size={32} />
        </div>
        <div>
          <h1>Talent Intelligence Dashboard</h1>
          <p>Real-time insights across your recruitment ecosystem</p>
        </div>
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon u-bg-blue"><Users size={20} /></div>
          <div className="stat-info">
            <span className="stat-label">Total Candidates</span>
            <span className="stat-value">{funnelData?.funnel?.total_candidates}</span>
          </div>
          <button 
            className="stat-view-btn" 
            onClick={() => navigate('/all-talent')}
            title="View all candidates"
          >
            View
          </button>
        </div>
        <div className="stat-card">
          <div className="stat-icon u-bg-green"><Briefcase size={20} /></div>
          <div className="stat-info">
            <span className="stat-label">Your Active Roles</span>
            <span className="stat-value">{skillDemand?.total_active_jobs || 0}</span>
          </div>
          <button 
            className="stat-view-btn" 
            onClick={() => navigate('/active-roles')}
            title="View active job postings"
          >
            View
          </button>
        </div>
        <div className="stat-card">
          <div className="stat-icon u-bg-purple"><Target size={20} /></div>
          <div className="stat-info">
            <span className="stat-label">Avg Match Score</span>
            <span className="stat-value">{(matchQuality?.averages?.overall * 100).toFixed(1)}%</span>
          </div>
        </div>
      </div>

      <div className="charts-main-grid">
        {/* Candidate Match Score Distribution */}
        <section className="chart-section wide">
          <div className="section-header">
            <BarChart2 size={18} />
            <h3>Candidate Match Score Distribution</h3>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart 
                data={distributionBarData}
                onClick={(data) => {
                  if (data && data.activePayload) {
                    const { min, max } = data.activePayload[0].payload;
                    navigate(`/matches?min_score=${min}&max_score=${max}`);
                  }
                }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="range" axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)', fontSize: 13}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)', fontSize: 13}} />
                <Tooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="custom-tooltip-premium">
                          <p className="tooltip-label">{payload[0].payload.range} Match</p>
                          <p className="tooltip-value">{payload[0].value} candidates in this range</p>
                          <p className="tooltip-hint">Click to filter candidates</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar 
                  dataKey="count" 
                  radius={[12, 12, 0, 0]}
                  animationDuration={1500}
                >
                  {distributionBarData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.color} 
                      style={{ cursor: 'pointer', filter: 'drop-shadow(0px 4px 10px rgba(0,0,0,0.2))' }}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <div className="intelligence-insight-box">
              <div className="insight-icon">💡</div>
              <p className="insight-text">{generateInsight()}</p>
            </div>
          </div>
        </section>

        {/* Recruitment Funnel */}
        <section className="chart-section">
          <div className="section-header">
            <TrendingUp size={18} />
            <h3>Recruitment Funnel</h3>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={funnelChartData}>
                <defs>
                  <linearGradient id="colorFunnel" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: 'var(--text-secondary)', fontSize: 11}} />
                <Tooltip />
                <Area type="monotone" dataKey="value" stroke="#6366f1" fillOpacity={1} fill="url(#colorFunnel)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Match Quality Distribution */}
        <section className="chart-section">
          <div className="section-header">
            <PieIcon size={18} />
            <h3>Match Quality Distribution</h3>
          </div>
          <div className="chart-container" style={{ display: 'flex', alignItems: 'center' }}>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={distributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  onClick={(data) => {
                    const rangeIdx = distributionData.findIndex(d => d.name === data.name);
                    const range = distributionBarData[rangeIdx];
                    if (range) {
                      navigate(`/matches?min_score=${range.min}&max_score=${range.max}`);
                    }
                  }}
                >
                  {distributionData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={COLORS[index % COLORS.length]} 
                      style={{ cursor: 'pointer' }}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="custom-legend">
              {distributionData.map((entry, index) => (
                <div key={entry.name} className="legend-item">
                  <span className="dot" style={{ backgroundColor: COLORS[index % COLORS.length] }}></span>
                  <span className="label">{entry.name}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}

export default AnalyticsDashboard
