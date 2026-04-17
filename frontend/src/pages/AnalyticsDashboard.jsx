import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from 'react-query'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, AreaChart, Area,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ComposedChart, Legend
} from 'recharts'
import {
  TrendingUp, Users, Briefcase, Target,
  PieChart as PieIcon, BarChart2, Activity, Zap
} from 'lucide-react'
import {
  getSkillDemand, getMatchQualityStats, getRecruitmentFunnel,
  getAdminStats, getAdminTrends
} from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import '../styles/Analytics.css'

/* ─── Palette visible on BOTH light & dark ─── */
const C = {
  indigo:  '#6366f1',
  emerald: '#10b981',
  amber:   '#f59e0b',
  rose:    '#f43f5e',
  violet:  '#8b5cf6',
  sky:     '#0ea5e9',
}
const ROLE_COLORS  = [C.indigo, C.emerald]
const MATCH_COLORS = [C.emerald, C.amber, C.sky, C.rose]

/* ─── Shared tooltip style (Glassmorphism & readable both themes) ─── */
const TT = {
  backgroundColor: 'rgba(15,23,42,0.85)',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255,255,255,0.15)',
  borderRadius: '12px',
  color: '#f1f5f9',
  fontSize: '13px',
  boxShadow: '0 12px 30px rgba(0,0,0,0.3)',
  padding: '12px 16px',
}

/* ─── Custom Tooltip Label ─── */
const ChartTip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={TT}>
      <p style={{ margin: '0 0 10px', fontWeight: 700, color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</p>
      {payload.map((p, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', margin: '6px 0', gap: '16px' }}>
          <span style={{ color: p.color || '#e2e8f0', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: '50%', backgroundColor: p.color }}></span>
            {p.name}
          </span>
          <strong style={{ color: '#fff', fontSize: '14px' }}>{p.value}</strong>
        </div>
      ))}
    </div>
  )
}

const AnalyticsDashboard = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'

  const { data: skillDemand,  isLoading: lS } = useQuery('skillDemand',       () => getSkillDemand().then(r => r.data))
  const { data: matchQuality, isLoading: lQ } = useQuery('matchQuality',       () => getMatchQualityStats().then(r => r.data))
  const { data: funnelData,   isLoading: lF } = useQuery('recruitmentFunnel',  () => getRecruitmentFunnel().then(r => r.data))
  const { data: adminStats,   isLoading: lA } = useQuery('adminOverview',      () => getAdminStats().then(r => r.data),      { enabled: isAdmin })
  const { data: trendData,    isLoading: lT } = useQuery('adminTrends',        () => getAdminTrends(30).then(r => r.data),   { enabled: isAdmin })

  if (lS || lQ || lF || (isAdmin && (lA || lT))) {
    return (
      <div className="analytics-loading">
        <div className="premium-loader" />
        <p>{isAdmin ? 'Gathering platform intelligence…' : 'Crunching intelligence data…'}</p>
      </div>
    )
  }

  const stats  = adminStats
  const isDemo = trendData?.[0]?.is_demo

  /* ══ Admin chart data ══ */
  const roleData = [
    { name: 'Candidates', value: stats?.job_seekers || 0 },
    { name: 'Recruiters', value: stats?.recruiters  || 0 },
  ]

  const overviewBarData = [
    { label: 'Candidates', value: stats?.job_seekers  || 0, fill: C.indigo },
    { label: 'Recruiters', value: stats?.recruiters   || 0, fill: C.emerald },
    { label: 'Live Jobs',  value: stats?.active_jobs  || 0, fill: C.amber },
    { label: 'Matches',    value: stats?.total_matches|| 0, fill: C.violet },
  ].sort((a, b) => b.value - a.value)

  const healthData = [
    { metric: 'Users',   value: Math.min(100, ((stats?.total_users  || 0) / 50)  * 100) },
    { metric: 'Jobs',    value: Math.min(100, ((stats?.total_jobs   || 0) / 30)  * 100) },
    { metric: 'Matches', value: Math.min(100, ((stats?.total_matches|| 0) / 100) * 100) },
    { metric: 'Active',  value: Math.min(100, ((stats?.active_jobs  || 0) / 20)  * 100) },
    { metric: 'Uptime',  value: 99 },
    { metric: 'Health',  value: 92 },
  ]

  const last14 = (trendData || []).slice(-14)
  const combinedData = last14.map(d => ({
    date: d.date,
    users: (d.seekers || 0) + (d.recruiters || 0),
    jobs:  d.jobs || 0,
  }))

  /* ══ Recruiter chart data ══ */
  const distBar = [
    { range: '80-100%', count: matchQuality?.score_distribution?.excellent_80_plus || 0, fill: C.emerald },
    { range: '60-80%',  count: matchQuality?.score_distribution?.good_60_80        || 0, fill: C.amber },
    { range: '40-60%',  count: matchQuality?.score_distribution?.fair_40_60        || 0, fill: C.sky },
    { range: '<40%',    count: matchQuality?.score_distribution?.low_under_40      || 0, fill: C.rose },
  ]
  const distPie = distBar.map((d, i) => ({ name: d.range, value: d.count, color: d.fill }))

  const funnelLine = [
    { name: 'Matches',   v: funnelData?.funnel?.total_matches_generated || 0 },
    { name: 'Applied',   v: funnelData?.funnel?.applied   || 0 },
    { name: 'Screened',  v: funnelData?.funnel?.screened  || 0 },
    { name: 'Interview', v: funnelData?.funnel?.interview || 0 },
    { name: 'Offered',   v: funnelData?.funnel?.offered   || 0 },
    { name: 'Hired',     v: funnelData?.funnel?.hired     || 0 },
  ]

  /* shared axis tick style */
  const tick = { fill: 'var(--adm-tick)', fontSize: 11 }
  const grid = { strokeDasharray: '3 3', vertical: false, stroke: 'var(--adm-grid)' }

  return (
    <div className="analytics-dashboard page-container">

      {/* ── Header ── */}
      <header className="analytics-header">
        <div className="header-icon-box">
          {isAdmin ? <Activity size={28} /> : <TrendingUp size={28} />}
        </div>
        <div>
          <h1>{isAdmin ? 'Platform Analytics Center' : 'Talent Intelligence Dashboard'}</h1>
          <p>{isAdmin ? 'Real-time multi-dimensional platform intelligence' : 'Real-time insights across your recruitment ecosystem'}</p>
        </div>
        {isAdmin && isDemo && <span className="demo-badge">Simulation Mode</span>}
      </header>

      {/* ══════════ ADMIN VIEW ══════════ */}
      {isAdmin && (
        <div className="adm-grid">

          {/* 1 ── Platform Overview (Horizontal Bar — replaces stat cards) */}
          <div className="adm-card adm-col-2">
            <div className="adm-card-hdr">
              <BarChart2 size={16} className="c-indigo" />
              <h3>Platform Overview</h3>
              <span className="adm-total-badge">Total Users: {stats?.total_users || 0}</span>
            </div>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={overviewBarData} layout="vertical" barSize={20}>
                <CartesianGrid {...grid} horizontal={false} vertical />
                <XAxis type="number" stroke="var(--adm-tick)" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis type="category" dataKey="label" stroke="var(--adm-tick)" fontSize={12} tickLine={false} axisLine={false} width={72} />
                <Tooltip cursor={{ fill: 'rgba(99,102,241,0.05)' }} content={<ChartTip />} />
                <Bar dataKey="value" radius={[0, 8, 8, 0]} animationDuration={1200} animationEasing="ease-out">
                  {overviewBarData.map((d, i) => <Cell key={i} fill={d.fill} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 2 ── User Role Donut */}
          <div className="adm-card">
            <div className="adm-card-hdr">
              <PieIcon size={16} className="c-emerald" />
              <h3>User Roles</h3>
            </div>
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie data={roleData} cx="50%" cy="50%" innerRadius={48} outerRadius={70} paddingAngle={4} dataKey="value" startAngle={90} endAngle={-270} animationDuration={1000} stroke="none">
                  {roleData.map((_, i) => <Cell key={i} fill={ROLE_COLORS[i]} strokeWidth={0} />)}
                </Pie>
                <Tooltip content={<ChartTip />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="adm-donut-legend">
              {roleData.map((d, i) => (
                <div key={d.name} className="adm-leg-row">
                  <span className="adm-leg-dot" style={{ background: ROLE_COLORS[i] }} />
                  <span>{d.name}</span>
                  <strong>{d.value}</strong>
                </div>
              ))}
            </div>
          </div>

          {/* 3 ── User Acquisition Area (30D) */}
          <div className="adm-card adm-col-3">
            <div className="adm-card-hdr">
              <TrendingUp size={16} className="c-indigo" />
              <h3>User Acquisition <span className="adm-period">30 Days</span></h3>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={trendData || []}>
                <defs>
                  <linearGradient id="gS" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%"   stopColor={C.indigo}  stopOpacity={0.65} />
                    <stop offset="100%" stopColor={C.indigo}  stopOpacity={0.05} />
                  </linearGradient>
                  <linearGradient id="gR" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%"   stopColor={C.emerald} stopOpacity={0.65} />
                    <stop offset="100%" stopColor={C.emerald} stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--adm-grid)" />
                <XAxis dataKey="date" tick={tick} tickLine={false} axisLine={false} interval="preserveStartEnd" />
                <YAxis tick={tick} tickLine={false} axisLine={false} />
                <Tooltip cursor={{ fill: 'rgba(99,102,241,0.05)' }} content={<ChartTip />} />
                <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 13, paddingTop: 10 }} />
                <Area type="monotone" dataKey="seekers"    name="Candidates" stroke={C.indigo}  strokeWidth={3} fill="url(#gS)" dot={false} activeDot={{ r: 6, strokeWidth: 0, fill: C.indigo }} animationDuration={1500} />
                <Area type="monotone" dataKey="recruiters" name="Recruiters" stroke={C.emerald} strokeWidth={3} fill="url(#gR)" dot={false} activeDot={{ r: 6, strokeWidth: 0, fill: C.emerald }} animationDuration={1500} />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* 4 ── Job Velocity Bar (14D) */}
          <div className="adm-card adm-col-2">
            <div className="adm-card-hdr">
              <Briefcase size={16} className="c-amber" />
              <h3>Job Posting Velocity <span className="adm-period">Last 14 Days</span></h3>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={last14} barSize={18} barCategoryGap="25%">
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--adm-grid)" />
                <XAxis dataKey="date" tick={tick} tickLine={false} axisLine={false} interval={1} />
                <YAxis tick={tick} tickLine={false} axisLine={false} />
                <Tooltip cursor={{ fill: 'rgba(99,102,241,0.05)' }} content={<ChartTip />} />
                <Bar dataKey="jobs" name="New Jobs" radius={[6, 6, 0, 0]} animationDuration={1000}>
                  {last14.map((_, i) => (
                    <Cell key={i} fill={`hsl(${38 + i * 6}, 88%, 52%)`} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 5 ── Platform Health Radar */}
          <div className="adm-card">
            <div className="adm-card-hdr">
              <Activity size={16} className="c-violet" />
              <h3>Platform Health</h3>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <RadarChart data={healthData} outerRadius="75%">
                <PolarGrid stroke="var(--adm-grid)" strokeDasharray="3 3" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: 'var(--adm-tick)', fontSize: 12, fontWeight: 600 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar name="Score" dataKey="value" stroke={C.violet} fill={C.violet} fillOpacity={0.45} strokeWidth={2.5} />
                <Tooltip content={<ChartTip />} formatter={(v) => [`${Math.round(v)}%`, 'Score']} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* 6 ── Combined Activity Composed (full width) */}
          <div className="adm-card adm-col-3">
            <div className="adm-card-hdr">
              <Zap size={16} className="c-rose" />
              <h3>Combined Activity: New Users vs New Jobs <span className="adm-period">Last 14 Days</span></h3>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <ComposedChart data={combinedData} barCategoryGap="30%">
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--adm-grid)" />
                <XAxis dataKey="date" tick={tick} tickLine={false} axisLine={false} interval={1} />
                <YAxis tick={tick} tickLine={false} axisLine={false} />
                <Tooltip content={<ChartTip />} />
                <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
                <Bar dataKey="jobs" name="New Jobs" fill={C.amber} radius={[6, 6, 0, 0]} barSize={16} />
                <Line type="monotone" dataKey="users" name="New Users" stroke={C.indigo} strokeWidth={3} dot={{ r: 5, fill: C.indigo, strokeWidth: 0 }} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

        </div>
      )}

      {/* ══════════ RECRUITER VIEW ══════════ */}
      {!isAdmin && (
        <>
          {/* Recruiter KPI row */}
          <div className="stats-grid" style={{ marginBottom: '2rem' }}>
            <div className="stat-card">
              <div className="stat-icon u-bg-blue"><Users size={20} /></div>
              <div className="stat-info">
                <span className="stat-label">Total Candidates</span>
                <span className="stat-value">{funnelData?.funnel?.total_candidates || 0}</span>
              </div>
              <button className="stat-view-btn" onClick={() => navigate('/all-talent')}>View</button>
            </div>
            <div className="stat-card">
              <div className="stat-icon u-bg-green"><Briefcase size={20} /></div>
              <div className="stat-info">
                <span className="stat-label">Active Roles</span>
                <span className="stat-value">{skillDemand?.total_active_jobs || 0}</span>
              </div>
              <button className="stat-view-btn" onClick={() => navigate('/active-roles')}>View</button>
            </div>
            <div className="stat-card">
              <div className="stat-icon u-bg-purple"><Target size={20} /></div>
              <div className="stat-info">
                <span className="stat-label">Avg Match Score</span>
                <span className="stat-value">{((matchQuality?.averages?.overall || 0) * 100).toFixed(1)}%</span>
              </div>
            </div>
          </div>

          <div className="charts-main-grid">
            {/* Match Score Distribution Bar */}
            <section className="chart-section wide">
              <div className="section-header">
                <BarChart2 size={18} />
                <h3>Match Score Distribution</h3>
              </div>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={distBar}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--adm-grid)" />
                    <XAxis dataKey="range" tick={tick} tickLine={false} axisLine={false} />
                    <YAxis tick={tick} tickLine={false} axisLine={false} />
                    <Tooltip cursor={{ fill: 'rgba(99,102,241,0.05)' }} content={<ChartTip />} />
                    <Bar dataKey="count" name="Candidates" radius={[10, 10, 0, 0]} animationDuration={1000} animationEasing="ease-out">
                      {distBar.map((d, i) => <Cell key={i} fill={d.fill} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>

            {/* Recruitment Funnel Line */}
            <section className="chart-section">
              <div className="section-header">
                <TrendingUp size={18} />
                <h3>Recruitment Funnel</h3>
              </div>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={funnelLine}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--adm-grid)" />
                    <XAxis dataKey="name" tick={tick} tickLine={false} axisLine={false} />
                    <YAxis tick={tick} tickLine={false} axisLine={false} />
                    <Tooltip cursor={{ fill: 'rgba(99,102,241,0.05)' }} content={<ChartTip />} />
                    <Line type="monotone" dataKey="v" name="Count" stroke={C.indigo} strokeWidth={3} dot={{ r: 5, fill: C.indigo, strokeWidth: 0 }} activeDot={{ r: 8, strokeWidth: 0, fill: C.indigo }} animationDuration={1500} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>

            {/* Match Quality Donut */}
            <section className="chart-section">
              <div className="section-header">
                <PieIcon size={18} />
                <h3>Match Quality Scale</h3>
              </div>
              <div className="chart-container">
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie data={distPie} cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={3} dataKey="value" animationDuration={1000} stroke="none">
                      {distPie.map((d, i) => <Cell key={i} fill={d.color} />)}
                    </Pie>
                    <Tooltip content={<ChartTip />} />
                    <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 13, paddingTop: 10 }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </section>
          </div>
        </>
      )}
    </div>
  )
}

export default AnalyticsDashboard
