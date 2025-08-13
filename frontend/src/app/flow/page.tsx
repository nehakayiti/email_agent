'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { FlowBucketTabs, BucketType } from '@/components/flow/flow-bucket-tabs';
import { FlowEmailList, FlowEmail } from '@/components/flow/flow-email-list';
import { getBucketCounts, getBucketEmails, BucketCounts } from '@/lib/api';

interface FlowDashboardState {
  activeBucket: BucketType;
  emails: FlowEmail[];
  counts: BucketCounts;
  loading: boolean;
  loadingEmails: boolean;
  loadingMore: boolean;
  hasMore: boolean;
  error: string | null;
  page: number;
}

const INITIAL_STATE: FlowDashboardState = {
  activeBucket: 'now',
  emails: [],
  counts: { now: 0, later: 0, reference: 0 },
  loading: true,
  loadingEmails: false,
  loadingMore: false,
  hasMore: true,
  error: null,
  page: 0
};

const EMAILS_PER_PAGE = 25;

export default function FlowDashboard() {
  const [state, setState] = useState<FlowDashboardState>(INITIAL_STATE);

  // Fetch bucket counts
  const fetchBucketCounts = useCallback(async () => {
    try {
      const counts = await getBucketCounts();
      setState(prev => ({ ...prev, counts, loading: false }));
    } catch (error) {
      console.error('Error fetching bucket counts:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to load bucket counts',
        loading: false
      }));
    }
  }, []);

  // Fetch emails for specific bucket
  const fetchBucketEmails = useCallback(async (
    bucket: BucketType,
    page: number = 0,
    append: boolean = false
  ) => {
    try {
      setState(prev => ({
        ...prev,
        loadingEmails: !append,
        loadingMore: append,
        error: null
      }));

      const offset = page * EMAILS_PER_PAGE;
      const newEmails = await getBucketEmails(bucket, EMAILS_PER_PAGE, offset, 'date');
      const hasMore = newEmails.length === EMAILS_PER_PAGE;

      setState(prev => ({
        ...prev,
        emails: append ? [...prev.emails, ...newEmails] : newEmails,
        hasMore,
        loadingEmails: false,
        loadingMore: false,
        page: page
      }));
    } catch (error) {
      console.error('Error fetching bucket emails:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : `Failed to load ${bucket} emails`,
        loadingEmails: false,
        loadingMore: false
      }));
    }
  }, []);

  // Handle bucket change
  const handleBucketChange = useCallback((bucket: BucketType) => {
    setState(prev => ({
      ...prev,
      activeBucket: bucket,
      emails: [],
      page: 0,
      hasMore: true,
      error: null
    }));
    fetchBucketEmails(bucket, 0, false);
  }, [fetchBucketEmails]);

  // Handle load more
  const handleLoadMore = useCallback(() => {
    const nextPage = state.page + 1;
    fetchBucketEmails(state.activeBucket, nextPage, true);
  }, [state.activeBucket, state.page, fetchBucketEmails]);

  // Handle email click
  const handleEmailClick = useCallback((email: FlowEmail) => {
    // Navigate to email detail page
    window.open(`/emails/${email.id}`, '_blank');
  }, []);

  // Handle refresh
  const handleRefresh = useCallback(() => {
    fetchBucketCounts();
    fetchBucketEmails(state.activeBucket, 0, false);
  }, [state.activeBucket, fetchBucketCounts, fetchBucketEmails]);

  // Initial load
  useEffect(() => {
    fetchBucketCounts();
    fetchBucketEmails('now', 0, false);
  }, [fetchBucketCounts, fetchBucketEmails]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">FlowMail</h1>
              <p className="text-gray-600 text-sm mt-1">Organize by urgency, not category</p>
            </div>
            
            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={state.loading || state.loadingEmails}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg
                className={`w-4 h-4 mr-2 ${state.loading || state.loadingEmails ? 'animate-spin' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error State */}
        {state.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  Error loading email data
                </h3>
                <p className="mt-1 text-sm text-red-700">{state.error}</p>
                <div className="mt-2">
                  <button
                    onClick={handleRefresh}
                    className="text-sm text-red-800 underline hover:no-underline"
                  >
                    Try again
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Flow Bucket Tabs */}
        <FlowBucketTabs
          activeBucket={state.activeBucket}
          counts={state.counts}
          onBucketChange={handleBucketChange}
          loading={state.loading}
        />

        {/* Flow Email List */}
        <div className="mt-8">
          <FlowEmailList
            emails={state.emails}
            bucketType={state.activeBucket}
            loading={state.loadingEmails}
            onEmailClick={handleEmailClick}
            onLoadMore={handleLoadMore}
            hasMore={state.hasMore}
            loadingMore={state.loadingMore}
          />
        </div>

        {/* Quick Stats Footer */}
        {!state.loading && !state.error && (
          <div className="mt-12 bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Stats</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600">{state.counts.now}</div>
                <div className="text-sm text-gray-600">High Priority</div>
                <div className="text-xs text-gray-500 mt-1">Need attention now</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-600">{state.counts.later}</div>
                <div className="text-sm text-gray-600">Medium Priority</div>
                <div className="text-xs text-gray-500 mt-1">Can be scheduled</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">{state.counts.reference}</div>
                <div className="text-sm text-gray-600">Low Priority</div>
                <div className="text-xs text-gray-500 mt-1">Reference material</div>
              </div>
            </div>
          </div>
        )}

        {/* Help Text */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            FlowMail organizes your emails by attention urgency.{' '}
            <span className="font-medium">NOW</span> emails need immediate attention,{' '}
            <span className="font-medium">LATER</span> emails can be scheduled, and{' '}
            <span className="font-medium">REFERENCE</span> emails are for future reference.
          </p>
        </div>
      </div>
    </div>
  );
}