import React, { useState, useRef, useEffect } from 'react';
import { InformationCircleIcon } from '@heroicons/react/24/outline';
import { get_attention_level, get_attention_color } from '../../lib/attention-utils';

interface AttentionScoreDetailsProps {
  score: number;
  isRead: boolean;
  labels: string[];
  showScore?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

interface ScoreBreakdown {
  baseScore: number;
  unreadBonus: number;
  importantBonus: number;
  starredBonus: number;
  totalScore: number;
}

function calculateScoreBreakdown(isRead: boolean, labels: string[]): ScoreBreakdown {
  const baseScore = 50.0;
  const unreadBonus = !isRead ? 15.0 : 0;
  const importantBonus = labels.includes('IMPORTANT') ? 30.0 : 0;
  const starredBonus = labels.includes('STARRED') ? 20.0 : 0;
  const totalScore = Math.max(0.0, Math.min(100.0, baseScore + unreadBonus + importantBonus + starredBonus));

  return {
    baseScore,
    unreadBonus,
    importantBonus,
    starredBonus,
    totalScore
  };
}

export function AttentionScoreDetails({ 
  score, 
  isRead,
  labels,
  showScore = true, 
  size = 'md',
  className = '' 
}: AttentionScoreDetailsProps) {
  const [showDetails, setShowDetails] = useState(false);
  const popoverRef = useRef<HTMLDivElement>(null);
  const level = get_attention_level(score);
  const color = get_attention_color(score);
  const breakdown = calculateScoreBreakdown(isRead, labels);
  
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base'
  };
  
  const colorClasses = {
    red: 'bg-red-100 text-red-800 border-red-200 hover:bg-red-200',
    orange: 'bg-orange-100 text-orange-800 border-orange-200 hover:bg-orange-200',
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-200 hover:bg-yellow-200',
    green: 'bg-green-100 text-green-800 border-green-200 hover:bg-green-200'
  };
  
  const emojiMap = {
    Critical: '🔴',
    High: '🟠',
    Medium: '🟡',
    Low: '🟢'
  };

  // Close popover when clicking outside
  useEffect(() => {
    if (!showDetails) return;
    
    function handleClick(e: MouseEvent) {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setShowDetails(false);
      }
    }
    
    function handleKey(e: KeyboardEvent) {
      if (e.key === 'Escape') setShowDetails(false);
    }
    
    document.addEventListener('mousedown', handleClick);
    document.addEventListener('keydown', handleKey);
    
    return () => {
      document.removeEventListener('mousedown', handleClick);
      document.removeEventListener('keydown', handleKey);
    };
  }, [showDetails]);

  return (
    <div className="relative">
      <button
        data-testid="attention-score-badge"
        className={`
          inline-flex items-center gap-1.5 rounded-full border font-medium transition-colors cursor-pointer
          ${sizeClasses[size]}
          ${colorClasses[color as keyof typeof colorClasses]}
          ${className}
        `}
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setShowDetails(!showDetails);
        }}
        title="Click to see attention score breakdown"
      >
        <span className="text-sm">{emojiMap[level as keyof typeof emojiMap]}</span>
        {showScore && (
          <span className="font-semibold">{score.toFixed(0)}</span>
        )}
        <span className="hidden sm:inline">{level}</span>
        <InformationCircleIcon className="h-3 w-3 opacity-60" />
      </button>

      {showDetails && (
        <div 
          ref={popoverRef}
          className="absolute left-0 top-full mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50 p-4"
          role="dialog"
          tabIndex={-1}
        >
          <div className="flex justify-between items-center mb-3">
            <h3 className="font-semibold text-gray-800 flex items-center gap-2">
              <InformationCircleIcon className="h-5 w-5 text-blue-500" />
              Attention Score Breakdown
            </h3>
            <button
              onClick={() => setShowDetails(false)}
              className="text-gray-400 hover:text-gray-600 text-lg leading-none"
              aria-label="Close"
            >
              ×
            </button>
          </div>

          <div className="space-y-3">
            {/* Current Score */}
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2">
                <span className="text-2xl">{emojiMap[level as keyof typeof emojiMap]}</span>
                <div>
                  <div className="font-semibold text-gray-800">{level} Priority</div>
                  <div className="text-sm text-gray-600">Score: {score.toFixed(1)}</div>
                </div>
              </div>
            </div>

            {/* Score Components */}
            <div className="space-y-2">
              <h4 className="font-medium text-gray-700 text-sm">Score Components:</h4>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Base Score</span>
                  <span className="font-medium">+{breakdown.baseScore}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className={`${breakdown.unreadBonus > 0 ? 'text-blue-600 font-medium' : 'text-gray-400'}`}>
                    {breakdown.unreadBonus > 0 ? '✓' : '✗'} Unread Email
                  </span>
                  <span className={`font-medium ${breakdown.unreadBonus > 0 ? 'text-blue-600' : 'text-gray-400'}`}>
                    +{breakdown.unreadBonus}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className={`${breakdown.importantBonus > 0 ? 'text-red-600 font-medium' : 'text-gray-400'}`}>
                    {breakdown.importantBonus > 0 ? '✓' : '✗'} Important Label
                  </span>
                  <span className={`font-medium ${breakdown.importantBonus > 0 ? 'text-red-600' : 'text-gray-400'}`}>
                    +{breakdown.importantBonus}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className={`${breakdown.starredBonus > 0 ? 'text-yellow-600 font-medium' : 'text-gray-400'}`}>
                    {breakdown.starredBonus > 0 ? '✓' : '✗'} Starred Label
                  </span>
                  <span className={`font-medium ${breakdown.starredBonus > 0 ? 'text-yellow-600' : 'text-gray-400'}`}>
                    +{breakdown.starredBonus}
                  </span>
                </div>
                
                <hr className="my-2" />
                
                <div className="flex justify-between items-center font-semibold">
                  <span className="text-gray-800">Total Score</span>
                  <span className="text-gray-800">{breakdown.totalScore}</span>
                </div>
              </div>
            </div>

            {/* Priority Levels */}
            <div className="mt-4 pt-3 border-t border-gray-200">
              <h4 className="font-medium text-gray-700 text-sm mb-2">Priority Levels:</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center gap-1">
                  <span>🟢</span>
                  <span className="text-gray-600">Low (0-29)</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>🟡</span>
                  <span className="text-gray-600">Medium (30-59)</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>🟠</span>
                  <span className="text-gray-600">High (60-79)</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>🔴</span>
                  <span className="text-gray-600">Critical (80-100)</span>
                </div>
              </div>
            </div>

            {/* Active Labels */}
            {labels.length > 0 && (
              <div className="mt-4 pt-3 border-t border-gray-200">
                <h4 className="font-medium text-gray-700 text-sm mb-2">Active Labels:</h4>
                <div className="flex flex-wrap gap-1">
                  {labels.map((label, index) => (
                    <span 
                      key={index}
                      className={`px-2 py-1 text-xs rounded-full ${
                        label === 'IMPORTANT' ? 'bg-red-100 text-red-700' :
                        label === 'STARRED' ? 'bg-yellow-100 text-yellow-700' :
                        label === 'UNREAD' ? 'bg-blue-100 text-blue-700' :
                        'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {label}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default AttentionScoreDetails;