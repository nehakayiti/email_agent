'use client';

import { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
  Filler,
} from 'chart.js';
import { getVolumeAnalytics, type VolumeAnalytics } from '@/lib/api';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const defaultData: ChartData<'line'> = {
  labels: [],
  datasets: [{
    label: 'Email Volume',
    data: [],
    borderColor: 'rgb(168, 85, 247)',
    backgroundColor: 'rgba(168, 85, 247, 0.1)',
    fill: true,
    tension: 0.4,
  }],
};

export default function VolumeChart() {
  const [data, setData] = useState<ChartData<'line'>>(defaultData);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getVolumeAnalytics();
        if (!response.dates || !response.counts || response.dates.length === 0) {
          throw new Error('Invalid or empty data received');
        }

        setData({
          labels: response.dates,
          datasets: [{
            label: 'Email Volume',
            data: response.counts,
            borderColor: 'rgb(168, 85, 247)',
            backgroundColor: 'rgba(168, 85, 247, 0.1)',
            fill: true,
            tension: 0.4,
          }],
        });
      } catch (err) {
        setError('Failed to load volume data');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full text-red-500">
        {error}
      </div>
    );
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of Emails',
        },
      },
    },
  };

  return <Line data={data} options={options} />;
} 