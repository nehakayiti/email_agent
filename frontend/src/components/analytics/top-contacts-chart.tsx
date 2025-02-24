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
import { getTopContacts, type TopContactsAnalytics } from '@/lib/api';

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
    label: 'Email Count',
    data: [],
    backgroundColor: 'rgba(239, 68, 68, 0.8)',
    borderColor: 'rgb(239, 68, 68)',
    borderWidth: 1,
  }],
};

export default function TopContactsChart() {
  const [data, setData] = useState<ChartData<'bar'>>(defaultData);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getTopContacts();
        if (!response.contacts || !response.counts || response.contacts.length === 0) {
          throw new Error('Invalid or empty data received');
        }

        setData({
          labels: response.contacts,
          datasets: [{
            label: 'Email Count',
            data: response.counts,
            backgroundColor: 'rgba(239, 68, 68, 0.8)',
            borderColor: 'rgb(239, 68, 68)',
            borderWidth: 1,
          }],
        });
      } catch (err) {
        setError('Failed to load top contacts data');
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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500" />
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
    indexAxis: 'y' as const,
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
      x: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of Emails',
        },
      },
    },
  };

  return <Bar data={data} options={options} />;
} 