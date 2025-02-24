'use client';

import { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartData,
} from 'chart.js';
import { getResponseTimeAnalytics, type ResponseTimeAnalytics } from '@/lib/api';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const defaultData: ChartData<'bar'> = {
  labels: [],
  datasets: [{
    label: 'Average Response Time (hours)',
    data: [],
    backgroundColor: 'rgba(34, 197, 94, 0.8)',
    borderColor: 'rgb(34, 197, 94)',
    borderWidth: 1,
  }],
};

export default function ResponseTimeChart() {
  const [data, setData] = useState<ChartData<'bar'>>(defaultData);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getResponseTimeAnalytics();
        if (!response.periods || !response.averages || response.periods.length === 0) {
          throw new Error('Invalid or empty data received');
        }

        setData({
          labels: response.periods,
          datasets: [{
            label: 'Average Response Time (hours)',
            data: response.averages,
            backgroundColor: 'rgba(34, 197, 94, 0.8)',
            borderColor: 'rgb(34, 197, 94)',
            borderWidth: 1,
          }],
        });
      } catch (err) {
        setError('Failed to load response time data');
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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500" />
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
          text: 'Hours',
        },
      },
    },
  };

  return <Bar data={data} options={options} />;
} 