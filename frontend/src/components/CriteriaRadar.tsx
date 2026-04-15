import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { TCriterion } from '../types';

interface CriteriaRadarProps {
  criteria: TCriterion[];
}

export const CriteriaRadar: React.FC<CriteriaRadarProps> = ({ criteria }) => {
  // Нормализуем данные для радара в процентах
  const data = criteria.map(c => ({
    name: c.name.split(' ')[0], // Короткое имя для графика
    fullName: c.name,
    score: (c.score / c.max_score) * 100, // В проценты
    rawScore: c.score,
    maxScore: c.max_score,
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-xl text-sm">
          <p className="font-semibold text-slate-800 mb-1">{data.fullName}</p>
          <p className="text-blue-600 font-medium">
            Оценка: {data.rawScore} / {data.maxScore}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis 
            dataKey="name" 
            tick={{ fill: '#64748b', fontSize: 12, fontWeight: 500 }} 
          />
          <PolarRadiusAxis 
            angle={30} 
            domain={[0, 100]} 
            tick={false} 
            axisLine={false} 
          />
          <Tooltip content={<CustomTooltip />} />
          <Radar
            name="Баллы"
            dataKey="score"
            stroke="#3b82f6"
            strokeWidth={2}
            fill="#3b82f6"
            fillOpacity={0.4}
            activeDot={{ r: 6, fill: '#1d4ed8' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};
