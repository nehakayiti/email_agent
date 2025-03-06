'use client';

import { useState, useEffect } from 'react';
import { 
  getCategoriesApi, 
  initializeCategories, 
  addKeyword, 
  addSenderRule,
  createCategory,
  type Category,
  type CreateCategoryRequest
} from '@/lib/api';

// New category form component 
function NewCategoryForm({ onAddSuccess }: { onAddSuccess: () => void }) {
  const [name, setName] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState(50);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !displayName) return;

    setIsSubmitting(true);
    setError(null);
    
    try {
      const categoryData: CreateCategoryRequest = {
        name,
        display_name: displayName,
        description: description || undefined,
        priority
      };
      
      await createCategory(categoryData);
      
      // Reset form
      setName('');
      setDisplayName('');
      setDescription('');
      setPriority(50);
      
      // Notify parent to refresh the list
      onAddSuccess();
    } catch (err) {
      console.error('Error creating category:', err);
      setError('Failed to create category. It may already exist or there was a server error.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <h2 className="text-xl font-semibold mb-4">Add New Category</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 border border-red-200 rounded">
          {error}
        </div>
      )}
      
      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Internal Name (lowercase, no spaces)
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value.toLowerCase().replace(/\s+/g, '_'))}
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          placeholder="e.g. work_emails"
          required
        />
      </div>
      
      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Display Name
        </label>
        <input
          type="text"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          placeholder="e.g. Work Emails"
          required
        />
      </div>
      
      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Description
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          placeholder="Optional description"
          rows={3}
        />
      </div>
      
      <div className="mb-4">
        <label className="block text-gray-700 text-sm font-bold mb-2">
          Priority (lower number = higher priority)
        </label>
        <input
          type="number"
          min="1"
          max="100"
          value={priority}
          onChange={(e) => setPriority(parseInt(e.target.value))}
          className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        />
      </div>
      
      <button
        type="submit"
        disabled={isSubmitting || !name || !displayName}
        className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded disabled:opacity-50"
      >
        {isSubmitting ? 'Creating...' : 'Create Category'}
      </button>
    </form>
  );
}

export default function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isKeywordModalOpen, setIsKeywordModalOpen] = useState(false);
  const [isSenderRuleModalOpen, setIsSenderRuleModalOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [newKeyword, setNewKeyword] = useState('');
  const [newSenderRule, setNewSenderRule] = useState('');
  const [isDomain, setIsDomain] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [initializingCategories, setInitializingCategories] = useState(false);

  useEffect(() => {
    async function fetchCategories() {
      try {
        setLoading(true);
        const response = await getCategoriesApi();
        setCategories(response.data);
      } catch (err) {
        setError('Failed to load categories');
        console.error('Error fetching categories:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchCategories();
  }, [refreshTrigger]);

  const handleInitializeCategories = async () => {
    try {
      setInitializingCategories(true);
      await initializeCategories();
      setRefreshTrigger(prev => prev + 1); // Trigger a refresh
      alert('Categories initialized successfully');
    } catch (err) {
      console.error('Error initializing categories:', err);
      alert('Failed to initialize categories');
    } finally {
      setInitializingCategories(false);
    }
  };

  const handleAddKeyword = async () => {
    if (!selectedCategory || !newKeyword.trim()) return;
    
    try {
      await addKeyword(selectedCategory.name, newKeyword.trim());
      setNewKeyword('');
      setIsKeywordModalOpen(false);
      setRefreshTrigger(prev => prev + 1); // Trigger a refresh
      alert('Keyword added successfully');
    } catch (err) {
      console.error('Error adding keyword:', err);
      alert('Failed to add keyword');
    }
  };

  const handleAddSenderRule = async () => {
    if (!selectedCategory || !newSenderRule.trim()) return;
    
    try {
      await addSenderRule(selectedCategory.name, newSenderRule.trim(), isDomain);
      setNewSenderRule('');
      setIsSenderRuleModalOpen(false);
      setRefreshTrigger(prev => prev + 1); // Trigger a refresh
      alert('Sender rule added successfully');
    } catch (err) {
      console.error('Error adding sender rule:', err);
      alert('Failed to add sender rule');
    }
  };

  const handleCategoryAdded = () => {
    setRefreshTrigger(prev => prev + 1); // Refresh the list
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold mb-2">Email Categories</h1>
          <p className="text-gray-600">Manage your email categories and classification rules</p>
        </div>
        <button 
          onClick={handleInitializeCategories}
          disabled={initializingCategories}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded disabled:opacity-50"
        >
          {initializingCategories ? 'Initializing...' : 'Initialize Categories'}
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <h2 className="text-xl font-semibold mb-4">Existing Categories</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {categories.length === 0 ? (
                <div className="bg-yellow-50 border border-yellow-100 text-yellow-700 px-4 py-3 rounded">
                  No categories found. Initialize categories or create a new one.
                </div>
              ) : (
                categories.map((category) => (
                  <div 
                    key={category.id} 
                    className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow"
                  >
                    <h2 className="text-xl font-semibold mb-2">{category.display_name}</h2>
                    <p className="text-gray-600 mb-4">{category.description || 'No description'}</p>
                    <div className="flex justify-between text-sm text-gray-500">
                      <span>Priority: {category.priority}</span>
                      <span>{category.is_system ? 'System' : 'Custom'}</span>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between">
                      <div className="text-sm">
                        <span className="font-medium">Keywords:</span> {category.keyword_count}
                      </div>
                      <div className="text-sm">
                        <span className="font-medium">Sender Rules:</span> {category.sender_rule_count}
                      </div>
                    </div>
                    <div className="mt-4 flex space-x-2">
                      <button 
                        onClick={() => {
                          setSelectedCategory(category);
                          setIsKeywordModalOpen(true);
                        }}
                        className="text-sm bg-indigo-50 text-indigo-600 hover:bg-indigo-100 px-3 py-1 rounded"
                      >
                        Add Keyword
                      </button>
                      <button 
                        onClick={() => {
                          setSelectedCategory(category);
                          setIsSenderRuleModalOpen(true);
                        }}
                        className="text-sm bg-indigo-50 text-indigo-600 hover:bg-indigo-100 px-3 py-1 rounded"
                      >
                        Add Sender Rule
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
          
          <div className="lg:col-span-1">
            <NewCategoryForm onAddSuccess={handleCategoryAdded} />
          </div>
          
          {/* Keyword Modal */}
          {isKeywordModalOpen && selectedCategory && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
                <h3 className="text-xl font-semibold mb-4">Add Keyword to {selectedCategory.display_name}</h3>
                <div className="mb-4">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Keyword
                  </label>
                  <input
                    type="text"
                    value={newKeyword}
                    onChange={(e) => setNewKeyword(e.target.value)}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    placeholder="Enter keyword"
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <button
                    onClick={() => setIsKeywordModalOpen(false)}
                    className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddKeyword}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded"
                  >
                    Add Keyword
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Sender Rule Modal */}
          {isSenderRuleModalOpen && selectedCategory && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
                <h3 className="text-xl font-semibold mb-4">Add Sender Rule to {selectedCategory.display_name}</h3>
                <div className="mb-4">
                  <label className="block text-gray-700 text-sm font-bold mb-2">
                    Pattern
                  </label>
                  <input
                    type="text"
                    value={newSenderRule}
                    onChange={(e) => setNewSenderRule(e.target.value)}
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    placeholder={isDomain ? "example.com" : "keyword"}
                  />
                </div>
                <div className="mb-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={isDomain}
                      onChange={(e) => setIsDomain(e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-gray-700">Is Domain</span>
                  </label>
                </div>
                <div className="flex justify-end space-x-2">
                  <button
                    onClick={() => setIsSenderRuleModalOpen(false)}
                    className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddSenderRule}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded"
                  >
                    Add Sender Rule
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
} 