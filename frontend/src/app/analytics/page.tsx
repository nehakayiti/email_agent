'use client';

import { useState, useEffect } from 'react';
import SentimentChart from '@/components/analytics/sentiment-chart';
import ResponseTimeChart from '@/components/analytics/response-time-chart';
import VolumeChart from '@/components/analytics/volume-chart';
import TopContactsChart from '@/components/analytics/top-contacts-chart';

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900">Email Analytics Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Sentiment Analysis */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Sentiment Trends</h2>
          <div className="h-[300px]">
            <SentimentChart />
          </div>
        </div>

        {/* Response Time Analysis */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Response Time Analysis</h2>
          <div className="h-[300px]">
            <ResponseTimeChart />
          </div>
        </div>

        {/* Email Volume */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Email Volume Trends</h2>
          <div className="h-[300px]">
            <VolumeChart />
          </div>
        </div>

        {/* Top Contacts */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Top Contacts</h2>
          <div className="h-[300px]">
            <TopContactsChart />
          </div>
        </div>
      </div>
    </div>
  );
} 