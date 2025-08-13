'use client';

import React from 'react';
import { cn } from '@/lib/utils';

export type BucketType = 'now' | 'later' | 'reference';

interface BucketCounts {
  now: number;
  later: number;
  reference: number;
}

interface FlowBucketTabsProps {
  activeBucket: BucketType;
  counts: BucketCounts;
  onBucketChange: (bucket: BucketType) => void;
  loading?: boolean;
}

interface BucketTabConfig {
  key: BucketType;
  label: string;
  description: string;
  icon: string;
  color: {
    active: string;
    inactive: string;
    badge: string;
  };
}

const bucketConfigs: BucketTabConfig[] = [
  {
    key: 'now',
    label: 'NOW',
    description: 'High priority - needs immediate attention',
    icon: '🔥',
    color: {
      active: 'bg-red-100 text-red-800 border-red-300',
      inactive: 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-red-50 hover:text-red-700',
      badge: 'bg-red-500 text-white'
    }
  },
  {
    key: 'later',
    label: 'LATER',
    description: 'Medium priority - can be scheduled',
    icon: '⏰',
    color: {
      active: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      inactive: 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-yellow-50 hover:text-yellow-700',
      badge: 'bg-yellow-500 text-white'
    }
  },
  {
    key: 'reference',
    label: 'REFERENCE',
    description: 'Low priority - reference material',
    icon: '📚',
    color: {
      active: 'bg-green-100 text-green-800 border-green-300',
      inactive: 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-green-50 hover:text-green-700',
      badge: 'bg-green-500 text-white'
    }
  }
];

export function FlowBucketTabs({
  activeBucket,
  counts,
  onBucketChange,
  loading = false
}: FlowBucketTabsProps) {
  const totalEmails = counts.now + counts.later + counts.reference;
  
  return (
    <div className="w-full">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Email Flow</h1>
        <p className="text-gray-600 mt-1">
          Organize emails by urgency - {totalEmails} total emails
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-2 mb-6">
        {bucketConfigs.map((bucket) => {
          const isActive = activeBucket === bucket.key;
          const count = counts[bucket.key];
          
          return (
            <button
              key={bucket.key}
              onClick={() => onBucketChange(bucket.key)}
              disabled={loading}
              className={cn(
                'relative flex items-center space-x-3 px-4 py-3 rounded-lg border-2 transition-all duration-200',
                'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                isActive ? bucket.color.active : bucket.color.inactive
              )}
            >
              {/* Icon */}
              <span className="text-lg" role="img" aria-label={bucket.label}>
                {bucket.icon}
              </span>
              
              {/* Label and Count */}
              <div className="flex flex-col items-start">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-sm tracking-wide">
                    {bucket.label}
                  </span>
                  {/* Count Badge */}
                  <span
                    className={cn(
                      'inline-flex items-center justify-center px-2 py-0.5 rounded-full text-xs font-medium',
                      isActive ? bucket.color.badge : 'bg-gray-400 text-white'
                    )}
                  >
                    {loading ? '...' : count.toLocaleString()}
                  </span>
                </div>
                
                {/* Description - only show on active tab on mobile, always on desktop */}
                <span className={cn(
                  'text-xs text-left mt-0.5 transition-opacity',
                  isActive ? 'opacity-100' : 'opacity-70 hidden sm:block'
                )}>
                  {bucket.description}
                </span>
              </div>
              
              {/* Active Indicator */}
              {isActive && (
                <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1 w-2 h-2 bg-current rounded-full" />
              )}
            </button>
          );
        })}
      </div>

      {/* Progress Bar */}
      {totalEmails > 0 && (
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
            <span>Email Distribution</span>
            <span>{totalEmails} emails</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div className="h-full flex">
              {/* NOW segment */}
              <div
                className="bg-red-500 transition-all duration-500"
                style={{
                  width: `${totalEmails > 0 ? (counts.now / totalEmails) * 100 : 0}%`
                }}
                title={`${counts.now} high priority emails`}
              />
              {/* LATER segment */}
              <div
                className="bg-yellow-500 transition-all duration-500"
                style={{
                  width: `${totalEmails > 0 ? (counts.later / totalEmails) * 100 : 0}%`
                }}
                title={`${counts.later} medium priority emails`}
              />
              {/* REFERENCE segment */}
              <div
                className="bg-green-500 transition-all duration-500"
                style={{
                  width: `${totalEmails > 0 ? (counts.reference / totalEmails) * 100 : 0}%`
                }}
                title={`${counts.reference} low priority emails`}
              />
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-4">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading bucket data...</span>
        </div>
      )}
    </div>
  );
}