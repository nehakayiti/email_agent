import { useState } from 'react';
import { toast } from 'react-hot-toast';
import { addKeyword, addSenderRule } from '@/lib/api';

interface KeywordFormProps {
  categoryName: string;
  onAddSuccess: () => void;
}

export function KeywordForm({ categoryName, onAddSuccess }: KeywordFormProps) {
  const [keyword, setKeyword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyword.trim()) return;

    setIsSubmitting(true);
    
    try {
      await addKeyword(categoryName, keyword.trim());
      toast.success('Keyword added successfully');
      setKeyword('');
      onAddSuccess();
    } catch (error) {
      console.error('Error adding keyword:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to add keyword');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-gray-50 rounded-lg">
      <h3 className="text-lg font-medium">Add New Keyword</h3>
      
      <div>
        <label htmlFor="keyword" className="block text-sm font-medium text-gray-700 mb-1">
          Keyword
        </label>
        <input
          id="keyword"
          type="text"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          className="block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Enter keyword"
          required
        />
        <p className="mt-1 text-sm text-gray-500">
          Add words that should be associated with this category
        </p>
      </div>

      <button
        type="submit"
        disabled={isSubmitting || !keyword.trim()}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
      >
        {isSubmitting ? 'Adding...' : 'Add Keyword'}
      </button>
    </form>
  );
}

interface SenderRuleFormProps {
  categoryName: string;
  onAddSuccess: () => void;
}

export function SenderRuleForm({ categoryName, onAddSuccess }: SenderRuleFormProps) {
  const [pattern, setPattern] = useState('');
  const [isDomain, setIsDomain] = useState(true);
  const [weight, setWeight] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pattern.trim()) return;

    setIsSubmitting(true);
    
    try {
      await addSenderRule(categoryName, pattern.trim(), isDomain, weight);
      toast.success('Sender rule added successfully');
      setPattern('');
      setIsDomain(true);
      setWeight(1);
      onAddSuccess();
    } catch (error) {
      console.error('Error adding sender rule:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to add sender rule');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-gray-50 rounded-lg">
      <h3 className="text-lg font-medium">Add New Sender Rule</h3>
      
      <div>
        <label htmlFor="pattern" className="block text-sm font-medium text-gray-700 mb-1">
          Email Pattern
        </label>
        <input
          id="pattern"
          type="text"
          value={pattern}
          onChange={(e) => setPattern(e.target.value)}
          className="block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          placeholder={isDomain ? "example.com" : "@example.com"}
          required
        />
        <p className="mt-1 text-sm text-gray-500">
          {isDomain 
            ? "Enter a domain (e.g. 'example.com')" 
            : "Enter any part of the sender email (e.g. '@example.com', 'newsletter')"}
        </p>
      </div>

      <div className="flex items-center">
        <input
          id="isDomain"
          type="checkbox"
          checked={isDomain}
          onChange={(e) => setIsDomain(e.target.checked)}
          className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
        />
        <label htmlFor="isDomain" className="ml-2 block text-sm text-gray-700">
          This is a full domain
        </label>
      </div>

      <div>
        <label htmlFor="weight" className="block text-sm font-medium text-gray-700 mb-1">
          Weight (1-10)
        </label>
        <input
          id="weight"
          type="number"
          min="1"
          max="10"
          value={weight}
          onChange={(e) => setWeight(parseInt(e.target.value))}
          className="block w-full border border-gray-300 rounded-md px-3 py-2 shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
        />
        <p className="mt-1 text-sm text-gray-500">
          Higher weight = stronger influence on categorization
        </p>
      </div>

      <button
        type="submit"
        disabled={isSubmitting || !pattern.trim()}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
      >
        {isSubmitting ? 'Adding...' : 'Add Sender Rule'}
      </button>
    </form>
  );
} 