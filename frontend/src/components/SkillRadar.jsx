import React from 'react';
import {
    Radar, RadarChart, PolarGrid,
    PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer
} from 'recharts';

const SkillRadar = ({ candidateSkills, jobRequirements }) => {
    // Process data for the radar chart
    const data = jobRequirements.slice(0, 8).map(skill => {
        const hasSkill = candidateSkills.some(cs => cs.toLowerCase() === skill.toLowerCase());
        return {
            subject: skill,
            A: hasSkill ? 100 : 20, // Candidate score
            fullMark: 100,
        };
    });

    if (data.length < 3) return <div className="insufficient-data">Matching skills to visualize...</div>;

    return (
        <div style={{ width: '100%', height: 300, background: 'rgba(255,255,255,0.5)', borderRadius: '16px', padding: '10px' }}>
            <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis
                        dataKey="subject"
                        tick={{ fill: '#64748b', fontSize: 12, fontWeight: 500 }}
                    />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar
                        name="Skills Match"
                        dataKey="A"
                        stroke="#7c3aed"
                        fill="#7c3aed"
                        fillOpacity={0.6}
                    />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default SkillRadar;
