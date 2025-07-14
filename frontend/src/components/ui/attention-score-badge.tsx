import React from 'react';
import { get_attention_level, get_attention_color } from '../../lib/attention-utils';

interface AttentionScoreBadgeProps {
  score: number;
  showScore?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function AttentionScoreBadge({ 
  score, 
  showScore = true, 
  size = 'md',
  className = '' 
}: AttentionScoreBadgeProps) {
  const level = get_attention_level(score);
  const color = get_attention_color(score);
  
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base'
  };
  
  const colorClasses = {
    red: 'bg-red-100 text-red-800 border-red-200',
    orange: 'bg-orange-100 text-orange-800 border-orange-200',
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    green: 'bg-green-100 text-green-800 border-green-200'
  };
  
  const emojiMap = {
    Critical: '🔴',
    High: '🟠',
    Medium: '🟡',
    Low: '🟢'
  };
  
  return (
    <div 
      data-testid="attention-score-badge"
      className={`
        inline-flex items-center gap-1.5 rounded-full border font-medium
        ${sizeClasses[size]}
        ${colorClasses[color as keyof typeof colorClasses]}
        ${className}
      `}
      title={`Attention Score: ${score.toFixed(1)} (${level})`}
    >
      <span className="text-sm">{emojiMap[level as keyof typeof emojiMap]}</span>
      {showScore && (
        <span className="font-semibold">{score.toFixed(0)}</span>
      )}
      <span className="hidden sm:inline">{level}</span>
    </div>
  );
}

export default AttentionScoreBadge; 