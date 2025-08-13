'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { BucketType } from './flow-bucket-tabs';

export interface FlowEmail {
  id: string;
  gmail_id: string;
  subject: string | null;
  from_email: string | null;
  received_at: string | null;
  snippet: string | null;
  labels: string[] | null;
  is_read: boolean;
  attention_score: number;
  category: string | null;
}

interface FlowEmailListProps {
  emails: FlowEmail[];
  bucketType: BucketType;
  loading?: boolean;
  onEmailClick?: (email: FlowEmail) => void;
  onLoadMore?: () => void;
  hasMore?: boolean;
  loadingMore?: boolean;
}

function getAttentionScoreColor(score: number): string {
  if (score >= 80) return 'text-red-600 bg-red-50';
  if (score >= 60) return 'text-orange-600 bg-orange-50';
  if (score >= 30) return 'text-yellow-600 bg-yellow-50';
  return 'text-green-600 bg-green-50';
}

function getAttentionScoreLabel(score: number): string {
  if (score >= 80) return 'Critical';
  if (score >= 60) return 'High';
  if (score >= 30) return 'Medium';
  return 'Low';
}

function formatTimeAgo(dateString: string | null): string {
  if (!dateString) return 'Unknown';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffHours < 1) return 'Just now';
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
  return `${Math.floor(diffDays / 30)}mo ago`;
}

function formatDayHeader(dateString: string | null): string {
  if (!dateString) return 'Unknown Date';
  
  const date = new Date(dateString);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  
  // Format as YYYY-MM-DD for comparison
  const dateStr = date.toDateString();
  const todayStr = today.toDateString();
  const yesterdayStr = yesterday.toDateString();
  
  if (dateStr === todayStr) {
    return 'Today';
  } else if (dateStr === yesterdayStr) {
    return 'Yesterday';
  } else {
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  }
}

function groupEmailsByDay(emails: FlowEmail[]): { [day: string]: FlowEmail[] } {
  const groups: { [day: string]: FlowEmail[] } = {};
  
  emails.forEach(email => {
    const dayKey = email.received_at ? 
      new Date(email.received_at).toDateString() : 
      'Unknown Date';
    
    if (!groups[dayKey]) {
      groups[dayKey] = [];
    }
    
    groups[dayKey].push(email);
  });
  
  // Sort emails within each day by attention score (descending)
  Object.keys(groups).forEach(dayKey => {
    groups[dayKey].sort((a, b) => b.attention_score - a.attention_score);
  });
  
  return groups;
}

function getBucketContext(bucketType: BucketType): {
  emptyMessage: string;
  emptyDescription: string;
  icon: string;
} {
  switch (bucketType) {
    case 'now':
      return {
        emptyMessage: 'No urgent emails',
        emptyDescription: 'All caught up! No high-priority emails need immediate attention.',
        icon: '✅'
      };
    case 'later':
      return {
        emptyMessage: 'No emails for later',
        emptyDescription: 'No medium-priority emails are scheduled for later attention.',
        icon: '📭'
      };
    case 'reference':
      return {
        emptyMessage: 'No reference emails',
        emptyDescription: 'No low-priority emails are stored for reference.',
        icon: '📚'
      };
  }
}

function FlowEmailCard({ email, bucketType, onClick }: {
  email: FlowEmail;
  bucketType: BucketType;
  onClick?: (email: FlowEmail) => void;
}) {
  const scoreColor = getAttentionScoreColor(email.attention_score);
  const scoreLabel = getAttentionScoreLabel(email.attention_score);
  const timeAgo = formatTimeAgo(email.received_at);
  
  return (
    <div
      className={cn(
        'group bg-white rounded-lg border border-gray-200 p-4 hover:border-gray-300 hover:shadow-sm transition-all duration-200',
        onClick && 'cursor-pointer',
        !email.is_read && 'bg-blue-50/30 border-blue-200'
      )}
      onClick={() => onClick?.(email)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        {/* Sender and Subject */}
        <div className="flex-1 min-w-0 mr-4">
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-sm font-medium text-gray-900 truncate">
              {email.from_email || 'Unknown Sender'}
            </span>
            {!email.is_read && (
              <span className="inline-block w-2 h-2 bg-blue-500 rounded-full" />
            )}
          </div>
          <h3 className={cn(
            'text-base truncate',
            email.is_read ? 'text-gray-700' : 'text-gray-900 font-medium'
          )}>
            {email.subject || 'No Subject'}
          </h3>
        </div>
        
        {/* Attention Score Badge */}
        <div className="flex items-center space-x-2 flex-shrink-0">
          <span className={cn(
            'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold',
            scoreColor
          )}>
            {Math.round(email.attention_score)} {scoreLabel}
          </span>
        </div>
      </div>
      
      {/* Snippet */}
      {email.snippet && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {email.snippet}
        </p>
      )}
      
      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        {/* Time and Category */}
        <div className="flex items-center space-x-3">
          <span>{timeAgo}</span>
          {email.category && (
            <>
              <span>•</span>
              <span className="capitalize">{email.category.toLowerCase()}</span>
            </>
          )}
        </div>
        
        {/* Labels */}
        {email.labels && email.labels.length > 0 && (
          <div className="flex items-center space-x-1">
            {email.labels.slice(0, 3).map((label) => (
              <span
                key={label}
                className="inline-block px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
              >
                {label}
              </span>
            ))}
            {email.labels.length > 3 && (
              <span className="text-gray-400">+{email.labels.length - 3}</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export function FlowEmailList({
  emails,
  bucketType,
  loading = false,
  onEmailClick,
  onLoadMore,
  hasMore = false,
  loadingMore = false
}: FlowEmailListProps) {
  const bucketContext = getBucketContext(bucketType);
  
  // Loading state
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg border border-gray-200 p-4 animate-pulse">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
                <div className="h-5 bg-gray-200 rounded w-3/4"></div>
              </div>
              <div className="h-6 bg-gray-200 rounded-full w-16"></div>
            </div>
            <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3 mb-3"></div>
            <div className="flex justify-between">
              <div className="h-3 bg-gray-200 rounded w-24"></div>
              <div className="h-3 bg-gray-200 rounded w-16"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }
  
  // Empty state
  if (emails.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4" role="img">
          {bucketContext.icon}
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          {bucketContext.emptyMessage}
        </h3>
        <p className="text-gray-600 max-w-md mx-auto">
          {bucketContext.emptyDescription}
        </p>
      </div>
    );
  }
  
  // Group emails by day
  const emailGroups = groupEmailsByDay(emails);
  const sortedDays = Object.keys(emailGroups).sort((a, b) => {
    // Sort days in descending order (most recent first)
    const dateA = new Date(a === 'Unknown Date' ? 0 : a);
    const dateB = new Date(b === 'Unknown Date' ? 0 : b);
    return dateB.getTime() - dateA.getTime();
  });

  return (
    <div className="space-y-6">
      {/* Email Count Header */}
      <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
        <span>{emails.length} email{emails.length !== 1 ? 's' : ''}</span>
        <span className="capitalize">{bucketType} priority</span>
      </div>
      
      {/* Grouped Email Cards by Day */}
      {sortedDays.map(dayKey => {
        const dayEmails = emailGroups[dayKey];
        const dayHeader = formatDayHeader(dayKey === 'Unknown Date' ? null : dayKey);
        
        return (
          <div key={dayKey} className="space-y-3">
            {/* Day Header */}
            <div className="sticky top-20 z-20 bg-gray-50 border-b border-gray-200 pb-2 mb-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">{dayHeader}</h3>
                <span className="text-sm text-gray-500">
                  {dayEmails.length} email{dayEmails.length !== 1 ? 's' : ''}
                </span>
              </div>
            </div>
            
            {/* Day's Email Cards */}
            <div className="space-y-3">
              {dayEmails.map((email) => (
                <FlowEmailCard
                  key={email.id}
                  email={email}
                  bucketType={bucketType}
                  onClick={onEmailClick}
                />
              ))}
            </div>
          </div>
        );
      })}
      
      {/* Load More Button */}
      {hasMore && (
        <div className="text-center pt-6">
          <button
            onClick={onLoadMore}
            disabled={loadingMore}
            className={cn(
              'inline-flex items-center px-6 py-3 border border-gray-300 rounded-lg text-sm font-medium',
              'bg-white text-gray-700 hover:bg-gray-50 hover:border-gray-400',
              'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'transition-all duration-200'
            )}
          >
            {loadingMore ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
                Loading more...
              </>
            ) : (
              <>
                Load more emails
                <svg className="ml-2 -mr-1 w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </>
            )}
          </button>
        </div>
      )}
      
      {/* Performance note for large lists */}
      {emails.length > 100 && (
        <div className="text-center text-xs text-gray-500 mt-4">
          Showing {emails.length} emails. Consider filtering for better performance.
        </div>
      )}
    </div>
  );
}