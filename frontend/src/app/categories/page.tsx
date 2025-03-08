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
  deleteCategory,
  trainTrashClassifier,
  getTrashClassifierStatus,
  bootstrapTrashClassifier,
  type Category,
  type CategoryKeyword,
  type SenderRule,
  type CreateCategoryRequest,
  type ClassifierStatus
} from '@/lib/api';
import { TrashIcon, BeakerIcon } from '@heroicons/react/24/outline';
import { EMAIL_SYNC_COMPLETED_EVENT } from '@/components/layout/main-layout';

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
  const [deletingCategory, setDeletingCategory] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [categoryToDelete, setCategoryToDelete] = useState<Category | null>(null);
  const [trainingClassifier, setTrainingClassifier] = useState(false);
  const [classifierStatus, setClassifierStatus] = useState<ClassifierStatus | null>(null);
  const [loadingClassifierStatus, setLoadingClassifierStatus] = useState(false);
  const [bootstrappingData, setBootstrappingData] = useState(false);

  useEffect(() => {
    async function fetchCategories() {
      try {
        setLoading(true);
        const response = await getCategoriesApi();
        console.log('Fetched categories:', response.data);
        console.log('Non-system categories:', response.data.filter(cat => !cat.is_system));
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

  useEffect(() => {
    // Fetch classifier status when the page loads
    fetchClassifierStatus();
  }, []);

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

  const handleTrainClassifier = async () => {
    try {
      setTrainingClassifier(true);
      await trainTrashClassifier();
      alert('Trash classifier training has been started in the background. This may take a few minutes.');
      
      // Refresh the status after a delay to give the training process time to start
      setTimeout(fetchClassifierStatus, 3000);
    } catch (err) {
      console.error('Error training classifier:', err);
      alert('Failed to train classifier');
    } finally {
      setTrainingClassifier(false);
    }
  };

  const handleBootstrapData = async () => {
    try {
      setBootstrappingData(true);
      await bootstrapTrashClassifier();
      alert('Successfully prepared training data from your 408+ trash emails. Starting training process now...');
      
      // After bootstrapping completes, automatically start the training process
      try {
        setTrainingClassifier(true);
        await trainTrashClassifier();
        alert('Training has started successfully! This may take a few minutes. The "Train Classifier" button will be enabled once training completes.');
      } catch (trainingErr) {
        console.error('Error starting training after bootstrap:', trainingErr);
        alert('Bootstrap completed successfully, but there was an error starting the training. Please try clicking the Train Classifier button manually.');
      } finally {
        setTrainingClassifier(false);
      }
      
      // Refresh the status after a delay to show updated event counts
      setTimeout(fetchClassifierStatus, 5000);
      // Then refresh again after a longer time to check if training completed
      setTimeout(fetchClassifierStatus, 20000);
    } catch (err) {
      console.error('Error bootstrapping training data:', err);
      alert('Failed to prepare training data from trash. Please try again or contact support if the issue persists.');
    } finally {
      setBootstrappingData(false);
    }
  };

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
        ✅ Reprocessing completed!
        
        📊 Summary:
        • Total emails: ${result.total}
        • Processed: ${result.processed}
        • Category changes: ${Object.keys(result.category_changes).length}
        • Emails moved to trash by ML: ${result.ml_classified_as_trash || 0}
        • Importance changes: ${result.importance_changes}
        • Duration: ${result.duration_seconds || 0}s
        
        The changes have been applied and will sync with Gmail on the next sync cycle.
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

  const handleDeleteCategory = async (category: Category) => {
    setCategoryToDelete(category);
    setShowDeleteConfirm(true);
  };

  const confirmDeleteCategory = async () => {
    if (!categoryToDelete) return;
    
    try {
      setDeletingCategory(categoryToDelete.name);
      await deleteCategory(categoryToDelete.name);
      setRefreshTrigger(prev => prev + 1); // Trigger a refresh
      
      // Dispatch an event to notify the layout that categories have changed
      // This will refresh the navigation sidebar
      const event = new CustomEvent(EMAIL_SYNC_COMPLETED_EVENT);
      window.dispatchEvent(event);
      
      alert(`Category "${categoryToDelete.display_name}" deleted successfully`);
    } catch (err) {
      console.error('Error deleting category:', err);
      if (err instanceof Error && err.message.includes('403')) {
        alert('System categories cannot be deleted');
      } else {
        alert('Failed to delete category');
      }
    } finally {
      setDeletingCategory(null);
      setShowDeleteConfirm(false);
      setCategoryToDelete(null);
    }
  };

  const handleCategoryAdded = () => {
    setRefreshTrigger(prev => prev + 1); // Refresh the list
    
    // Dispatch an event to notify the layout that categories have changed
    // This will refresh the navigation sidebar
    const event = new CustomEvent(EMAIL_SYNC_COMPLETED_EVENT);
    window.dispatchEvent(event);
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

      {/* New feature banner */}
      <div className="mb-8 bg-gradient-to-r from-purple-100 to-indigo-100 rounded-lg p-4 border border-purple-200 flex items-center">
        <div className="bg-purple-600 text-white p-2 rounded-full mr-4">
          <BeakerIcon className="h-6 w-6" />
        </div>
        <div>
          <h2 className="font-semibold text-purple-800">New Feature: ML-Powered Trash Detection</h2>
          <p className="text-purple-700 text-sm">
            Train our machine learning model to automatically identify trash emails based on your preferences.
            Scroll down to the <span className="font-semibold">Trash Email Classifier</span> section below.
          </p>
        </div>
      </div>

      {/* ML Classifier Status Panel */}
      <div className="mb-8 bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
          <div>
            <h2 className="text-xl font-semibold flex items-center">
              <BeakerIcon className="h-6 w-6 mr-2 text-purple-600" />
              Trash Email Classifier
            </h2>
            <p className="text-gray-600 mt-1">
              Machine learning model to identify trash emails based on content and user behavior
            </p>
          </div>
          <div className="mt-4 md:mt-0 text-center">
            <button 
              onClick={handleTrainClassifier}
              disabled={trainingClassifier || (classifierStatus?.trash_events_count || 0) < 10}
              className={`
                py-3 px-6 rounded flex items-center transition-all duration-200 transform hover:scale-105
                ${(classifierStatus?.trash_events_count || 0) >= 10 
                  ? 'bg-green-600 hover:bg-green-700 text-white font-medium shadow-md' 
                  : 'bg-gray-300 text-gray-700 cursor-not-allowed opacity-50'
                }
              `}
            >
              {trainingClassifier ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Training Model...</span>
                </>
              ) : (
                <>
                  <BeakerIcon className="h-5 w-5 mr-2" />
                  <span>{(classifierStatus?.trash_events_count || 0) >= 10 ? 'Train Trash Classifier' : 'Need More Training Data'}</span>
                </>
              )}
            </button>
            {(classifierStatus?.trash_events_count || 0) < 10 && (
              <div className="text-xs text-amber-600 mt-2 text-center">
                Need at least 10 trash events to train
              </div>
            )}
            {(classifierStatus?.trash_events_count || 0) >= 10 && !classifierStatus?.is_model_available && (
              <div className="text-xs text-green-600 mt-2 text-center">
                ✓ Ready to train! Click to start training
              </div>
            )}
          </div>
        </div>

        {loadingClassifierStatus ? (
          <div className="flex justify-center py-4">
            <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-purple-500"></div>
          </div>
        ) : classifierStatus ? (
          <>
            {/* Show bootstrap option if we have insufficient training data but there are likely existing trash emails */}
            {classifierStatus.trash_events_count < classifierStatus.recommended_min_events && (
              <div className="mb-4 p-4 bg-yellow-50 rounded border border-yellow-200">
                <div className="flex items-start">
                  <div className="bg-yellow-500 text-white p-2 rounded-full mr-3 mt-1">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-yellow-700">You have 408+ emails in Trash!</h3>
                    <p className="text-yellow-600 text-sm mt-1">
                      We can use your existing trash emails for training the classifier instead of waiting to collect more events.
                    </p>
                    <button
                      onClick={handleBootstrapData}
                      disabled={bootstrappingData}
                      className="mt-3 bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-2 px-4 rounded flex items-center disabled:opacity-50"
                    >
                      {bootstrappingData ? (
                        <>
                          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Processing...
                        </>
                      ) : (
                        'Use Existing Trash Emails'
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div className="bg-gray-50 p-4 rounded">
                <div className="font-medium text-gray-700">Status</div>
                <div className={`text-lg font-semibold ${classifierStatus.is_model_available ? 'text-green-600' : 'text-amber-600'}`}>
                  {classifierStatus.is_model_available ? 'Model Active' : 'Not Available'}
                </div>
                {classifierStatus.is_model_available && (
                  <div className="text-sm text-gray-600 mt-1">
                    ML model will be used during email processing
                  </div>
                )}
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <div className="font-medium text-gray-700">Training Data</div>
                <div className="flex items-center">
                  <div className="text-lg font-semibold">
                    {classifierStatus.trash_events_count} / {classifierStatus.recommended_min_events} events
                  </div>
                  <div className="ml-2">
                    {classifierStatus.trash_events_count >= classifierStatus.recommended_min_events ? 
                      <span className="text-green-500">✓</span> : 
                      <span className="text-amber-500">⚠️</span>
                    }
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                  <div className="bg-purple-600 h-2.5 rounded-full" style={{ 
                    width: `${Math.min(100, (classifierStatus.trash_events_count / classifierStatus.recommended_min_events) * 100)}%` 
                  }}></div>
                </div>
                {classifierStatus.trash_events_count < classifierStatus.recommended_min_events && (
                  <div className="text-xs text-amber-600 mt-1">
                    Move more emails to trash to improve training
                  </div>
                )}
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <div className="font-medium text-gray-700">Message</div>
                <div className="text-sm text-gray-600">{classifierStatus.message}</div>
                <div className="mt-2 text-xs text-blue-600">
                  Use "Reprocess All Emails" to apply the classifier to your existing emails
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="bg-gray-50 p-4 rounded text-gray-600 mb-4">
            Unable to fetch classifier status.
          </div>
        )}

        {/* Add visible training instructions */}
        <div className="mt-4 p-4 bg-blue-50 rounded border border-blue-200">
          <h3 className="text-md font-semibold text-blue-800 mb-2">How to Train Your Classifier</h3>
          <ol className="list-decimal list-inside text-sm text-blue-700 space-y-1">
            <li>If you have existing emails in Trash, click the <b>"Use Existing Trash Emails"</b> button (when available)</li>
            <li>Otherwise, move unwanted emails to <b>Trash</b> (at least 10 emails)</li>
            <li>Click the <b>Train Trash Classifier</b> button above (it will activate once you have enough data)</li>
            <li>After training, use <b>Reprocess All Emails</b> to apply the model to your emails</li>
          </ol>
          
          {/* Add a big, prominent button here for clarity */}
          {classifierStatus && classifierStatus.trash_events_count < classifierStatus.recommended_min_events && (
            <div className="mt-4 flex justify-center">
              <button
                onClick={handleBootstrapData}
                disabled={bootstrappingData}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-lg flex items-center disabled:opacity-50 shadow-md transform transition-transform hover:scale-105"
              >
                {bootstrappingData ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing Existing Trash...
                  </>
                ) : (
                  <>
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Use My 408+ Trash Emails for Training
                  </>
                )}
              </button>
            </div>
          )}
          
          <p className="text-xs text-blue-600 mt-2">
            The more emails you move to trash, the better the classifier will become at identifying unwanted emails.
          </p>
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
                    <h2 className="text-xl font-semibold mb-2">
                      {category.display_name}
                      <span className="ml-2 text-xs px-2 py-1 rounded bg-gray-100 text-gray-700">
                        {category.is_system ? 'System' : 'Custom'}
                      </span>
                    </h2>
                    <p className="text-gray-600 mb-4">{category.description || 'No description'}</p>
                    <div className="flex justify-between text-sm text-gray-500">
                      <span>Priority: {category.priority}</span>
                      <span>ID: {category.id}</span>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between">
                      <div className="text-sm">
                        <span className="font-medium">Keywords:</span> {category.keyword_count}
                      </div>
                      <div className="text-sm">
                        <span className="font-medium">Sender Rules:</span> {category.sender_rule_count}
                      </div>
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
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
                      
                      {/* Delete button - only shown for non-system categories */}
                      {!category.is_system && (
                        <button 
                          onClick={() => handleDeleteCategory(category)}
                          disabled={deletingCategory === category.name}
                          className="text-sm bg-red-50 text-red-600 hover:bg-red-100 px-3 py-1 rounded flex items-center"
                          title="Delete Category"
                        >
                          <TrashIcon className="h-4 w-4 mr-1" />
                          Delete
                        </button>
                      )}
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

          {/* Delete Confirmation Modal */}
          {showDeleteConfirm && categoryToDelete && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
                <h3 className="text-xl font-semibold mb-4">Delete Category</h3>
                <p className="mb-6">
                  Are you sure you want to delete the category "{categoryToDelete.display_name}"? 
                  This will remove all associated keywords and sender rules. 
                  Emails in this category will be moved to the primary category.
                </p>
                <div className="flex justify-end space-x-2">
                  <button
                    onClick={() => {
                      setShowDeleteConfirm(false);
                      setCategoryToDelete(null);
                    }}
                    className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-4 rounded"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={confirmDeleteCategory}
                    disabled={deletingCategory === categoryToDelete.name}
                    className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded disabled:opacity-50"
                  >
                    {deletingCategory === categoryToDelete.name ? 'Deleting...' : 'Delete Category'}
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