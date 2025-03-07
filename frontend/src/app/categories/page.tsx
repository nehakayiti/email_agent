'use client';

import { useState, useEffect } from 'react';
import { 
  getCategoriesApi, 
  initializeCategories, 
  addKeyword, 
  addSenderRule,
  createCategory,
  getCategoryKeywords,
  getCategorySenderRules,
  reprocessAllEmails,
  type Category,
  type CategoryKeyword,
  type SenderRule,
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
  const [isViewRulesModalOpen, setIsViewRulesModalOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [newKeyword, setNewKeyword] = useState('');
  const [newSenderRule, setNewSenderRule] = useState('');
  const [isDomain, setIsDomain] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [initializingCategories, setInitializingCategories] = useState(false);
  const [reprocessingEmails, setReprocessingEmails] = useState(false);
  const [selectedCategoryKeywords, setSelectedCategoryKeywords] = useState<CategoryKeyword[]>([]);
  const [selectedCategorySenderRules, setSelectedCategorySenderRules] = useState<SenderRule[]>([]);
  const [loadingRules, setLoadingRules] = useState(false);

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

  const handleReprocessEmails = async () => {
    try {
      setReprocessingEmails(true);
      const result = await reprocessAllEmails();
      
      // Show a more detailed alert with the results
      const message = `
        Reprocessing completed!
        Total emails: ${result.total}
        Processed: ${result.processed}
        Category changes: ${Object.keys(result.category_changes).length}
        Importance changes: ${result.importance_changes}
      `;
      
      alert(message);
    } catch (err) {
      console.error('Error reprocessing emails:', err);
      alert('Failed to reprocess emails');
    } finally {
      setReprocessingEmails(false);
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

  const handleViewRules = async (category: Category) => {
    try {
      setSelectedCategory(category);
      setLoadingRules(true);
      
      // Fetch the keywords and sender rules for the selected category
      const [keywordsResponse, senderRulesResponse] = await Promise.all([
        getCategoryKeywords(category.name),
        getCategorySenderRules(category.name)
      ]);
      
      setSelectedCategoryKeywords(keywordsResponse);
      setSelectedCategorySenderRules(senderRulesResponse);
      setIsViewRulesModalOpen(true);
    } catch (err) {
      console.error('Error fetching category rules:', err);
      alert('Failed to fetch category rules');
    } finally {
      setLoadingRules(false);
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
        <div className="flex space-x-4">
          <button 
            onClick={handleReprocessEmails}
            disabled={reprocessingEmails}
            className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded disabled:opacity-50"
          >
            {reprocessingEmails ? 'Reprocessing...' : 'Reprocess All Emails'}
          </button>
          <button 
            onClick={handleInitializeCategories}
            disabled={initializingCategories}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded disabled:opacity-50"
          >
            {initializingCategories ? 'Initializing...' : 'Initialize Categories'}
          </button>
        </div>
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
                      <button 
                        onClick={() => handleViewRules(category)}
                        className="text-sm bg-green-50 text-green-600 hover:bg-green-100 px-3 py-1 rounded"
                      >
                        View Rules
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
          
          {/* View Rules Modal */}
          {isViewRulesModalOpen && selectedCategory && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <h3 className="text-xl font-semibold mb-4">Rules for {selectedCategory.display_name}</h3>
                
                {loadingRules ? (
                  <div className="flex justify-center py-10">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-500"></div>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Keywords Section */}
                    <div>
                      <h4 className="text-lg font-medium mb-3">Keywords ({selectedCategoryKeywords.length})</h4>
                      {selectedCategoryKeywords.length === 0 ? (
                        <div className="bg-gray-50 p-4 rounded text-gray-600">
                          No keywords found for this category.
                        </div>
                      ) : (
                        <div className="bg-gray-50 p-4 rounded">
                          <ul className="divide-y divide-gray-200">
                            {selectedCategoryKeywords.map((keyword) => (
                              <li key={keyword.id} className="py-2">
                                <div className="flex items-center justify-between">
                                  <div className="font-medium">{keyword.keyword}</div>
                                  <div className="flex space-x-2 text-xs">
                                    {keyword.is_regex && (
                                      <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded">Regex</span>
                                    )}
                                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                                      Weight: {keyword.weight}
                                    </span>
                                    {keyword.user_id ? (
                                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded">User</span>
                                    ) : (
                                      <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded">System</span>
                                    )}
                                  </div>
                                </div>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                    
                    {/* Sender Rules Section */}
                    <div>
                      <h4 className="text-lg font-medium mb-3">Sender Rules ({selectedCategorySenderRules.length})</h4>
                      {selectedCategorySenderRules.length === 0 ? (
                        <div className="bg-gray-50 p-4 rounded text-gray-600">
                          No sender rules found for this category.
                        </div>
                      ) : (
                        <div className="bg-gray-50 p-4 rounded">
                          <ul className="divide-y divide-gray-200">
                            {selectedCategorySenderRules.map((rule) => (
                              <li key={rule.id} className="py-2">
                                <div className="flex items-center justify-between">
                                  <div className="font-medium">{rule.pattern}</div>
                                  <div className="flex space-x-2 text-xs">
                                    {rule.is_domain ? (
                                      <span className="px-2 py-1 bg-orange-100 text-orange-800 rounded">Domain</span>
                                    ) : (
                                      <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded">Substring</span>
                                    )}
                                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                                      Weight: {rule.weight}
                                    </span>
                                    {rule.user_id ? (
                                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded">User</span>
                                    ) : (
                                      <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded">System</span>
                                    )}
                                  </div>
                                </div>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                <div className="mt-6 flex justify-end">
                  <button
                    onClick={() => setIsViewRulesModalOpen(false)}
                    className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded"
                  >
                    Close
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