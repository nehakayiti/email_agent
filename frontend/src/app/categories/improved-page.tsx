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
  updateSenderRulePattern,
  updateSenderRuleWeight,
  deleteSenderRule,
  updateKeywordWeight,
  deleteKeyword,
  type ActionRule,
  type ActionRuleRequest
} from '@/lib/api';
import { KeywordForm, SenderRuleForm } from '@/components/ui/category-rule-forms';
import { ActionRuleDisplay } from '@/components/ui/action-rule-display';
import { ActionRuleSuggestions } from '@/components/ui/action-rule-suggestions';
import { ActionRuleModal } from '@/components/ui/action-rule-modal';
import { ActionEngineProvider, useActionEngine } from '@/lib/action-engine-context';
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
          data-testid="category-name-input"
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
          data-testid="category-display-name-input"
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
          data-testid="category-description-input"
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
        data-testid="save-category-btn"
      >
        {isSubmitting ? 'Creating...' : 'Create Category'}
      </button>
    </form>
  );
}

function CategoriesImprovedPageContent() {
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
  const [editingKeywordId, setEditingKeywordId] = useState<number | null>(null);
  const [editingSenderRuleId, setEditingSenderRuleId] = useState<number | null>(null);
  const [deletingKeywordId, setDeletingKeywordId] = useState<number | null>(null);
  const [deletingSenderRuleId, setDeletingSenderRuleId] = useState<number | null>(null);
  const [editKeyword, setEditKeyword] = useState('');
  const [editKeywordWeight, setEditKeywordWeight] = useState(1);
  const [editSenderPattern, setEditSenderPattern] = useState('');
  const [editSenderIsDomain, setEditSenderIsDomain] = useState(true);
  const [editSenderWeight, setEditSenderWeight] = useState(1);
  const [editLoading, setEditLoading] = useState(false);
  
  // Action Engine state
  const [showActionRuleModal, setShowActionRuleModal] = useState(false);
  const [editingActionRule, setEditingActionRule] = useState<ActionRule | null>(null);
  const [showActionSuggestions, setShowActionSuggestions] = useState(false);
  
  // Action Engine context
  const { 
    getRulesForCategory, 
    createRule, 
    updateRule, 
    deleteRule, 
    toggleRule 
  } = useActionEngine();

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
    
    console.log('🎯 Loading rules for category:', category.display_name);
    setSelectedCategory(category);
    setLoadingRules(true);
    
    try {
      const [keywords, senderRules] = await Promise.all([
        getCategoryKeywords(category.name),
        getCategorySenderRules(category.name)
      ]);
      
      // Sort: user-defined first, then system-defined
      keywords.sort((a, b) => (b.user_id ? 1 : 0) - (a.user_id ? 1 : 0));
      senderRules.sort((a, b) => (b.user_id ? 1 : 0) - (a.user_id ? 1 : 0));
      
      console.log('📝 Loaded keywords:', keywords.length);
      console.log('📧 Loaded sender rules:', senderRules.length);
      
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

  // Action Engine handlers
  const handleAddActionRule = () => {
    setEditingActionRule(null);
    setShowActionRuleModal(true);
  };

  const handleEditActionRule = (rule: ActionRule) => {
    setEditingActionRule(rule);
    setShowActionRuleModal(true);
  };

  const handlePreviewActionRule = (rule: ActionRule) => {
    // TODO: Implement preview functionality
    toast('Preview functionality coming soon!');
  };

  const handleToggleActionRule = async (rule: ActionRule, enabled: boolean) => {
    try {
      await toggleRule(rule.category_id, enabled);
    } catch (error) {
      console.error('Failed to toggle action rule:', error);
    }
  };

  const handleDeleteActionRule = async (rule: ActionRule) => {
    try {
      await deleteRule(rule.category_id);
    } catch (error) {
      console.error('Failed to delete action rule:', error);
    }
  };

  const handleSaveActionRule = async (rule: ActionRuleRequest) => {
    if (!selectedCategory) return;
    
    try {
      if (editingActionRule) {
        await updateRule(selectedCategory.id, rule);
      } else {
        await createRule(selectedCategory.id, rule);
      }
    } catch (error) {
      console.error('Failed to save action rule:', error);
      throw error;
    }
  };

  const handleSelectSuggestion = (suggestion: ActionRuleRequest) => {
    setEditingActionRule(null);
    setShowActionRuleModal(true);
    // The modal will handle the suggestion
  };

  return (
    <div className="container mx-auto px-4 py-8" data-testid="categories-page">
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
                data-testid="add-category-btn"
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
                <div className="space-y-8">
                  {/* Keywords Section */}
                  <section>
                    <div className="flex items-center mb-2">
                      <h3 className="text-lg font-semibold mr-2">Keywords</h3>
                      <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-xs font-medium">{categoryKeywords.length}</span>
                    </div>
                    {showKeywordForm && (
                      <div className="mb-4">
                        <KeywordForm 
                          categoryName={selectedCategory.name} 
                          onAddSuccess={refreshRules} 
                        />
                      </div>
                    )}
                    {categoryKeywords.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-8 text-gray-400">
                        <span className="text-4xl mb-2">🔍</span>
                        <span className="mb-2">No keywords defined for this category.</span>
                        <button
                          onClick={() => setShowKeywordForm(true)}
                          className="mt-2 px-3 py-1 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 text-sm font-medium"
                        >
                          Add your first keyword
                        </button>
                      </div>
                    ) : (
                      <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
                        <div className="flex items-center px-4 py-2 bg-gray-100 text-xs font-semibold uppercase tracking-wide sticky top-0 z-10 shadow-sm border-b border-gray-200">
                          <div className="flex-1">Keyword</div>
                          <div className="w-28 text-center border-l border-gray-200">Weight</div>
                          <div className="w-24 text-center border-l border-gray-200">Source</div>
                          <div className="w-24 text-right border-l border-gray-200">Actions</div>
                        </div>
                        {categoryKeywords.map((keyword) => (
                          <div
                            key={keyword.id}
                            className={`group flex items-center px-4 py-2 border-t border-gray-100 transition-colors relative ${editingKeywordId === keyword.id ? 'bg-yellow-50 border-l-4 border-yellow-400' : 'hover:bg-gray-50 hover:border-l-4 hover:border-indigo-400'}`}
                          >
                            {editingKeywordId === keyword.id ? (
                              <>
                                <input
                                  type="text"
                                  value={editKeyword}
                                  onChange={e => setEditKeyword(e.target.value)}
                                  className="flex-1 border rounded px-2 py-1 mr-2 text-base font-semibold"
                                />
                                <input
                                  type="number"
                                  min={1}
                                  max={10}
                                  value={editKeywordWeight}
                                  onChange={e => setEditKeywordWeight(Number(e.target.value))}
                                  className="w-20 border rounded px-2 py-1 text-center mr-2 text-base"
                                />
                                <div className="w-24 text-center"></div>
                                <div className="w-24 flex justify-end gap-2">
                                  <button
                                    onClick={async () => {
                                      setEditLoading(true);
                                      try {
                                        await updateKeywordWeight(keyword.id, editKeywordWeight);
                                        toast.success('Keyword updated');
                                        setEditingKeywordId(null);
                                        refreshRules();
                                      } catch (err) {
                                        toast.error('Failed to update keyword');
                                      } finally {
                                        setEditLoading(false);
                                      }
                                    }}
                                    className="text-green-700 hover:text-green-900 font-bold"
                                    disabled={editLoading}
                                    title="Save changes"
                                  >
                                    💾
                                  </button>
                                  <button
                                    onClick={() => setEditingKeywordId(null)}
                                    className="text-gray-500 hover:text-gray-700 font-bold"
                                    disabled={editLoading}
                                    title="Cancel"
                                  >
                                    ✖️
                                  </button>
                                </div>
                              </>
                            ) : (
                              <>
                                <div className="flex-1 flex items-center gap-2 font-semibold text-gray-900 text-base truncate">
                                  <span className="font-mono">{keyword.keyword}</span>
                                </div>
                                <div className="w-28 flex justify-center border-l border-gray-200">
                                  <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-gray-200 text-gray-700 font-medium shadow-sm" title="Keyword weight">
                                    <span>⚖️</span> {keyword.weight}
                                  </span>
                                </div>
                                <div className="w-24 flex justify-center border-l border-gray-200">
                                  <span
                                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium shadow-sm ${keyword.user_id ? 'bg-green-100 text-green-800' : 'bg-purple-100 text-purple-800'}`}
                                    title={keyword.user_id ? 'User-defined' : 'System-defined'}
                                  >
                                    <span>{keyword.user_id ? '👤' : '⚙️'}</span> {keyword.user_id ? 'User' : 'System'}
                                  </span>
                                </div>
                                <div className="w-24 flex justify-end gap-2 border-l border-gray-200 opacity-0 group-hover:opacity-100 transition-opacity">
                                  <button
                                    onClick={() => {
                                      setEditingKeywordId(keyword.id);
                                      setEditKeyword(keyword.keyword);
                                      setEditKeywordWeight(keyword.weight);
                                    }}
                                    className="text-indigo-500 hover:text-indigo-700"
                                    title="Edit keyword"
                                  >
                                    ✏️
                                  </button>
                                  {deletingKeywordId === keyword.id ? (
                                    <>
                                      <button
                                        onClick={async () => {
                                          setEditLoading(true);
                                          try {
                                            await deleteKeyword(keyword.id);
                                            toast.success('Keyword deleted');
                                            setDeletingKeywordId(null);
                                            refreshRules();
                                          } catch (err) {
                                            toast.error('Failed to delete keyword');
                                          } finally {
                                            setEditLoading(false);
                                          }
                                        }}
                                        className="text-red-600 hover:text-red-800 font-bold"
                                        disabled={editLoading}
                                        title="Confirm delete"
                                      >
                                        ✔️
                                      </button>
                                      <button
                                        onClick={() => setDeletingKeywordId(null)}
                                        className="text-gray-500 hover:text-gray-700 font-bold"
                                        disabled={editLoading}
                                        title="Cancel delete"
                                      >
                                        ✖️
                                      </button>
                                    </>
                                  ) : (
                                    <button
                                      onClick={() => setDeletingKeywordId(keyword.id)}
                                      className="text-red-500 hover:text-red-700"
                                      title="Delete keyword"
                                    >
                                      🗑️
                                    </button>
                                  )}
                                </div>
                              </>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </section>

                  {/* Sender Rules Section */}
                  <section>
                    <div className="flex items-center mb-2">
                      <h3 className="text-lg font-semibold mr-2">Sender Rules</h3>
                      <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-xs font-medium">{categorySenderRules.length}</span>
                    </div>
                    {showSenderRuleForm && (
                      <div className="mb-4">
                        <SenderRuleForm 
                          categoryName={selectedCategory.name} 
                          onAddSuccess={refreshRules} 
                        />
                      </div>
                    )}
                    {categorySenderRules.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-8 text-gray-400">
                        <span className="text-4xl mb-2">📬</span>
                        <span className="mb-2">No sender rules defined for this category.</span>
                        <button
                          onClick={() => setShowSenderRuleForm(true)}
                          className="mt-2 px-3 py-1 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 text-sm font-medium"
                        >
                          Add your first sender rule
                        </button>
                      </div>
                    ) : (
                      <div className="rounded-lg border border-gray-200 bg-white overflow-hidden mt-8">
                        <div className="flex items-center px-4 py-2 bg-gray-100 text-xs font-semibold uppercase tracking-wide sticky top-0 z-10 shadow-sm border-b border-gray-200">
                          <div className="flex-1">Pattern</div>
                          <div className="w-28 text-center border-l border-gray-200">Type</div>
                          <div className="w-28 text-center border-l border-gray-200">Weight</div>
                          <div className="w-24 text-center border-l border-gray-200">Source</div>
                          <div className="w-24 text-right border-l border-gray-200">Actions</div>
                        </div>
                        {categorySenderRules.map((rule) => (
                          <div
                            key={rule.id}
                            className={`group flex items-center px-4 py-2 border-t border-gray-100 transition-colors relative ${editingSenderRuleId === rule.id ? 'bg-yellow-50 border-l-4 border-yellow-400' : 'hover:bg-gray-50 hover:border-l-4 hover:border-indigo-400'}`}
                          >
                            {editingSenderRuleId === rule.id ? (
                              <>
                                <input
                                  type="text"
                                  value={editSenderPattern}
                                  onChange={e => setEditSenderPattern(e.target.value)}
                                  className="flex-1 border rounded px-2 py-1 mr-2 text-base font-semibold"
                                />
                                <select
                                  value={editSenderIsDomain ? 'domain' : 'substring'}
                                  onChange={e => setEditSenderIsDomain(e.target.value === 'domain')}
                                  className="w-24 border rounded px-2 py-1 text-center mr-2 text-base"
                                >
                                  <option value="domain">Domain</option>
                                  <option value="substring">Substring</option>
                                </select>
                                <input
                                  type="number"
                                  min={1}
                                  max={10}
                                  value={editSenderWeight}
                                  onChange={e => setEditSenderWeight(Number(e.target.value))}
                                  className="w-24 border rounded px-2 py-1 text-center mr-2 text-base"
                                />
                                <div className="w-24 text-center"></div>
                                <div className="w-24 flex justify-end gap-2">
                                  <button
                                    onClick={async () => {
                                      setEditLoading(true);
                                      try {
                                        await updateSenderRulePattern(rule.id, editSenderPattern, editSenderIsDomain);
                                        await updateSenderRuleWeight(rule.id, editSenderWeight);
                                        toast.success('Sender rule updated');
                                        setEditingSenderRuleId(null);
                                        refreshRules();
                                      } catch (err) {
                                        toast.error('Failed to update sender rule');
                                      } finally {
                                        setEditLoading(false);
                                      }
                                    }}
                                    className="text-green-700 hover:text-green-900 font-bold"
                                    disabled={editLoading}
                                    title="Save changes"
                                  >
                                    💾
                                  </button>
                                  <button
                                    onClick={() => setEditingSenderRuleId(null)}
                                    className="text-gray-500 hover:text-gray-700 font-bold"
                                    disabled={editLoading}
                                    title="Cancel"
                                  >
                                    ✖️
                                  </button>
                                </div>
                              </>
                            ) : (
                              <>
                                <div className="flex-1 flex items-center gap-2 font-semibold text-gray-900 text-base truncate">
                                  <span className="font-mono">{rule.pattern}</span>
                                </div>
                                <div className="w-28 flex justify-center border-l border-gray-200">
                                  <span
                                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium shadow-sm ${rule.is_domain ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-800'}`}
                                    title={rule.is_domain ? 'Domain match' : 'Substring match'}
                                  >
                                    <span>{rule.is_domain ? '🌐' : '#'}</span> {rule.is_domain ? 'Domain' : 'Substring'}
                                  </span>
                                </div>
                                <div className="w-28 flex justify-center border-l border-gray-200">
                                  <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-gray-200 text-gray-700 font-medium shadow-sm" title="Sender rule weight">
                                    <span>⚖️</span> {rule.weight}
                                  </span>
                                </div>
                                <div className="w-24 flex justify-center border-l border-gray-200">
                                  <span
                                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium shadow-sm ${rule.user_id ? 'bg-green-100 text-green-800' : 'bg-purple-100 text-purple-800'}`}
                                    title={rule.user_id ? 'User-defined' : 'System-defined'}
                                  >
                                    <span>{rule.user_id ? '👤' : '⚙️'}</span> {rule.user_id ? 'User' : 'System'}
                                  </span>
                                </div>
                                <div className="w-24 flex justify-end gap-2 border-l border-gray-200 opacity-0 group-hover:opacity-100 transition-opacity">
                                  <button
                                    onClick={() => {
                                      setEditingSenderRuleId(rule.id);
                                      setEditSenderPattern(rule.pattern);
                                      setEditSenderIsDomain(rule.is_domain);
                                      setEditSenderWeight(rule.weight);
                                    }}
                                    className="text-indigo-500 hover:text-indigo-700"
                                    title="Edit sender rule"
                                  >
                                    ✏️
                                  </button>
                                  {deletingSenderRuleId === rule.id ? (
                                    <>
                                      <button
                                        onClick={async () => {
                                          setEditLoading(true);
                                          try {
                                            await deleteSenderRule(rule.id);
                                            toast.success('Sender rule deleted');
                                            setDeletingSenderRuleId(null);
                                            refreshRules();
                                          } catch (err) {
                                            toast.error('Failed to delete sender rule');
                                          } finally {
                                            setEditLoading(false);
                                          }
                                        }}
                                        className="text-red-600 hover:text-red-800 font-bold"
                                        disabled={editLoading}
                                        title="Confirm delete"
                                      >
                                        ✔️
                                      </button>
                                      <button
                                        onClick={() => setDeletingSenderRuleId(null)}
                                        className="text-gray-500 hover:text-gray-700 font-bold"
                                        disabled={editLoading}
                                        title="Cancel delete"
                                      >
                                        ✖️
                                      </button>
                                    </>
                                  ) : (
                                    <button
                                      onClick={() => setDeletingSenderRuleId(rule.id)}
                                      className="text-red-500 hover:text-red-700"
                                      title="Delete sender rule"
                                    >
                                      🗑️
                                    </button>
                                  )}
                                </div>
                              </>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </section>

                  {/* Action Rules Section */}
                  <section>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center">
                        <h3 className="text-lg font-semibold mr-2">Action Rules</h3>
                        <span className="bg-purple-100 text-purple-800 px-2 py-0.5 rounded text-xs font-medium">
                          {getRulesForCategory(selectedCategory.id).length}
                        </span>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => setShowActionSuggestions(!showActionSuggestions)}
                          className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-1 px-3 rounded text-sm"
                        >
                          {showActionSuggestions ? 'Hide Suggestions' : 'Show Suggestions'}
                        </button>
                        <button
                          onClick={handleAddActionRule}
                          className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-1 px-3 rounded text-sm"
                        >
                          Add Action Rule
                        </button>
                      </div>
                    </div>

                    {showActionSuggestions && (
                      <ActionRuleSuggestions
                        categoryName={selectedCategory.display_name}
                        onSelectSuggestion={handleSelectSuggestion}
                      />
                    )}

                    {(() => {
                      const rules = getRulesForCategory(selectedCategory.id);
                      console.log('🔧 Action Rules for category:', selectedCategory.display_name, 'Rules:', rules);
                      return (
                        <ActionRuleDisplay
                          rules={rules}
                          categoryId={selectedCategory.id}
                          categoryName={selectedCategory.display_name}
                          onEdit={handleEditActionRule}
                          onPreview={handlePreviewActionRule}
                          onToggle={handleToggleActionRule}
                          onAddRule={handleAddActionRule}
                          onDeleteRule={handleDeleteActionRule}
                        />
                      );
                    })()}
                  </section>
                </div>
              )}

              {/* Action Rule Modal */}
              {selectedCategory && (
                <ActionRuleModal
                  isOpen={showActionRuleModal}
                  onClose={() => setShowActionRuleModal(false)}
                  categoryId={selectedCategory.id}
                  categoryName={selectedCategory.display_name}
                  initialRule={editingActionRule || undefined}
                  onSave={handleSaveActionRule}
                />
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

export default function CategoriesImprovedPage() {
  return (
    <ActionEngineProvider>
      <CategoriesImprovedPageContent />
    </ActionEngineProvider>
  );
} 