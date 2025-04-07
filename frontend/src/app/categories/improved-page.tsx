'use client';

import { useState, useEffect } from 'react';
import { 
  getCategoriesApi, 
  initializeCategories, 
  createCategory,
  getCategoryKeywords,
  getCategorySenderRules,
  reprocessAllEmails,
  trainTrashClassifier,
  getTrashClassifierStatus,
  bootstrapTrashClassifier,
  evaluateTrashClassifier,
  getClassifierMetrics,
  type Category,
  type CategoryKeyword,
  type SenderRule,
  type CreateCategoryRequest,
  type ClassifierStatus,
  type ModelMetrics,
} from '@/lib/api';
import { CategoryManage } from '@/components/ui/category-manage';
import { KeywordForm, SenderRuleForm } from '@/components/ui/category-rule-forms';
import { toast } from 'react-hot-toast';

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
      toast.success('Category created successfully');
    } catch (err) {
      console.error('Error creating category:', err);
      setError('Failed to create category. It may already exist or there was a server error.');
      toast.error('Failed to create category');
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

export default function CategoriesImprovedPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [initializingCategories, setInitializingCategories] = useState(false);
  const [reprocessingEmails, setReprocessingEmails] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [categoryKeywords, setCategoryKeywords] = useState<CategoryKeyword[]>([]);
  const [categorySenderRules, setCategorySenderRules] = useState<SenderRule[]>([]);
  const [loadingRules, setLoadingRules] = useState(false);
  const [showNewCategoryForm, setShowNewCategoryForm] = useState(false);
  const [showKeywordForm, setShowKeywordForm] = useState(false);
  const [showSenderRuleForm, setShowSenderRuleForm] = useState(false);
  const [classifierStatus, setClassifierStatus] = useState<ClassifierStatus | null>(null);
  const [loadingClassifierStatus, setLoadingClassifierStatus] = useState(false);

  useEffect(() => {
    fetchCategories();
    fetchClassifierStatus();
  }, [refreshTrigger]);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const response = await getCategoriesApi();
      // Sort by priority (lower number = higher priority)
      setCategories(response.data.sort((a, b) => a.priority - b.priority));
    } catch (err) {
      setError('Failed to load categories');
      console.error('Error fetching categories:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchClassifierStatus = async () => {
    try {
      setLoadingClassifierStatus(true);
      const status = await getTrashClassifierStatus();
      setClassifierStatus(status);
    } catch (err) {
      console.error('Error fetching classifier status:', err);
    } finally {
      setLoadingClassifierStatus(false);
    }
  };

  const handleInitializeCategories = async () => {
    try {
      setInitializingCategories(true);
      await initializeCategories();
      setRefreshTrigger(prev => prev + 1);
      toast.success('Categories initialized successfully');
    } catch (err) {
      console.error('Error initializing categories:', err);
      toast.error('Failed to initialize categories');
    } finally {
      setInitializingCategories(false);
    }
  };

  const handleReprocessEmails = async () => {
    try {
      setReprocessingEmails(true);
      const result = await reprocessAllEmails();
      toast.success(`Reprocessing completed! ${result.processed} emails updated.`);
    } catch (err) {
      console.error('Error reprocessing emails:', err);
      toast.error('Failed to reprocess emails');
    } finally {
      setReprocessingEmails(false);
    }
  };

  const loadCategoryRules = async (category: Category) => {
    if (!category) return;
    
    setSelectedCategory(category);
    setLoadingRules(true);
    
    try {
      const [keywords, senderRules] = await Promise.all([
        getCategoryKeywords(category.name),
        getCategorySenderRules(category.name)
      ]);
      
      setCategoryKeywords(keywords);
      setCategorySenderRules(senderRules);
    } catch (err) {
      console.error('Error loading category rules:', err);
      toast.error('Failed to load category rules');
    } finally {
      setLoadingRules(false);
    }
  };

  const refreshRules = async () => {
    if (selectedCategory) {
      await loadCategoryRules(selectedCategory);
    }
  };

  const handleCategoryAdded = () => {
    setRefreshTrigger(prev => prev + 1);
    setShowNewCategoryForm(false);
  };

  const handleCategoryDeleted = () => {
    setRefreshTrigger(prev => prev + 1);
    setSelectedCategory(null);
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

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Categories</h2>
              <button
                onClick={() => setShowNewCategoryForm(!showNewCategoryForm)}
                className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-1 px-3 rounded text-sm"
              >
                {showNewCategoryForm ? 'Cancel' : 'Add New'}
              </button>
            </div>
            
            {showNewCategoryForm && (
              <div className="mb-6">
                <NewCategoryForm onAddSuccess={handleCategoryAdded} />
              </div>
            )}
            
            {loading ? (
              <div className="p-4 text-center">Loading categories...</div>
            ) : (
              <ul className="divide-y">
                {categories.map(category => (
                  <li 
                    key={category.id}
                    className={`py-3 px-2 cursor-pointer hover:bg-gray-50 ${selectedCategory?.id === category.id ? 'bg-indigo-50' : ''}`}
                    onClick={() => loadCategoryRules(category)}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <span className="font-medium">{category.display_name}</span>
                        <p className="text-sm text-gray-500">{category.description}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                          Rules: {category.keyword_count + category.sender_rule_count}
                        </span>
                        <span className={`px-2 py-1 rounded text-xs ${category.is_system ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'}`}>
                          {category.is_system ? 'System' : 'User'}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="lg:col-span-2">
          {selectedCategory ? (
            <div>
              <div className="mb-4 flex justify-between items-center">
                <h2 className="text-xl font-semibold">Manage {selectedCategory.display_name}</h2>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setShowKeywordForm(!showKeywordForm)}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-1 px-3 rounded text-sm"
                  >
                    {showKeywordForm ? 'Cancel' : 'Add Keyword'}
                  </button>
                  <button
                    onClick={() => setShowSenderRuleForm(!showSenderRuleForm)}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-1 px-3 rounded text-sm"
                  >
                    {showSenderRuleForm ? 'Cancel' : 'Add Sender Rule'}
                  </button>
                </div>
              </div>

              {loadingRules ? (
                <div className="p-4 text-center">Loading rules...</div>
              ) : (
                <>
                  {showKeywordForm && (
                    <div className="mb-6">
                      <KeywordForm 
                        categoryName={selectedCategory.name} 
                        onAddSuccess={refreshRules} 
                      />
                    </div>
                  )}
                  
                  {showSenderRuleForm && (
                    <div className="mb-6">
                      <SenderRuleForm 
                        categoryName={selectedCategory.name} 
                        onAddSuccess={refreshRules} 
                      />
                    </div>
                  )}
                  
                  <CategoryManage 
                    category={selectedCategory}
                    senderRules={categorySenderRules}
                    keywords={categoryKeywords}
                    onDelete={handleCategoryDeleted}
                    onRefresh={refreshRules}
                  />
                </>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-8 border border-gray-200 text-center">
              <h3 className="text-lg font-medium text-gray-600 mb-2">No Category Selected</h3>
              <p className="text-gray-500">
                Select a category from the list to manage its rules
              </p>
            </div>
          )}
        </div>
      </div>
      
      {/* Classifier Status */}
      <div className="mt-8 bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <h2 className="text-xl font-semibold mb-4">ML Classifier Status</h2>
        {loadingClassifierStatus ? (
          <div className="p-4 text-center">Loading classifier status...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-medium mb-2">Model Status</h3>
              <div className={`px-3 py-2 rounded ${classifierStatus?.is_model_available ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {classifierStatus?.is_model_available ? 'Available' : 'Not Trained'}
              </div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-medium mb-2">Training Data</h3>
              <div className="px-3 py-2 bg-blue-100 text-blue-800 rounded">
                {classifierStatus?.training_data_count || 0} emails
              </div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-medium mb-2">Last Trained</h3>
              <div className="px-3 py-2 bg-gray-100 text-gray-800 rounded">
                {classifierStatus?.last_trained || 'Never'}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 