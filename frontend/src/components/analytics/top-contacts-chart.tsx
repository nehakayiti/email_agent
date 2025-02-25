'use client';

import { useState, useEffect } from 'react';
import { getTopContacts, type TopContactsAnalytics } from '@/lib/api';

interface Contact {
  email: string;
  count: number;
}

export default function TopContactsChart() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getTopContacts();
        if (!response.contacts || !response.counts || response.contacts.length === 0) {
          throw new Error('Invalid or empty data received');
        }

        const contactData = response.contacts.map((email, index) => ({
          email,
          count: response.counts[index]
        }));

        setContacts(contactData);
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

  return (
    <div className="overflow-x-auto overflow-y-auto h-full">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50 sticky top-0 z-10">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Email Count
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Contact
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {contacts.map((contact, index) => (
            <tr key={contact.email} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {contact.count}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {contact.email}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 