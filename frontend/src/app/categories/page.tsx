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
  evaluateTrashClassifier,
  getClassifierMetrics,
  type Category,
  type CategoryKeyword,
  type SenderRule as ApiSenderRule,
  type CreateCategoryRequest,
  type ClassifierStatus,
  type ModelMetrics,
  updateSenderRuleWeight
} from '@/lib/api';
import { TrashIcon, BeakerIcon } from '@heroicons/react/24/outline';
import { EMAIL_SYNC_COMPLETED_EVENT } from '@/components/layout/main-layout';
import { toast } from 'react-hot-toast';

// Extend the SenderRule type to include the isOverridden flag
interface SenderRule extends ApiSenderRule {
  isOverridden?: boolean;
}

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

// ML Classifier Configuration Component
function MLClassifierConfig({ 
  onTrain, 
  onBootstrap, 
  classifierStatus,
  isTraining,
  isBootstrapping 
}: { 
  onTrain: (testSize: number) => void,
  onBootstrap: (testSize: number) => void,
  classifierStatus: ClassifierStatus | null,
  isTraining: boolean,
  isBootstrapping: boolean
}) {
  const [testSize, setTestSize] = useState(0.2);

  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200 mb-4">
      <h3 className="font-medium text-gray-800 mb-2">Training Configuration</h3>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Test Data Split
        </label>
        <div className="flex items-center">
          <input
            type="range"
            min="0.1"
            max="0.4"
            step="0.05"
            value={testSize}
            onChange={(e) => setTestSize(parseFloat(e.target.value))}
            className="w-full mr-3"
          />
          <span className="text-sm text-gray-600 w-16">{Math.round(testSize * 100)}%</span>
        </div>
        <p className="text-xs text-gray-500 mt-1">
          Percentage of data reserved for testing model performance
        </p>
      </div>
      
      <div className="flex space-x-2">
        <button
          onClick={() => onTrain(testSize)}
          disabled={isTraining || (classifierStatus?.trash_events_count || 0) < 10}
          className={`
            py-2 px-4 rounded text-sm flex items-center
            ${(classifierStatus?.trash_events_count || 0) >= 10 
              ? 'bg-green-600 hover:bg-green-700 text-white' 
              : 'bg-gray-300 text-gray-700 cursor-not-allowed'}
          `}
        >
          {isTraining ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Training...
            </>
          ) : 'Train Model'}
        </button>
        
        <button
          onClick={() => onBootstrap(testSize)}
          disabled={isBootstrapping}
          className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded text-sm flex items-center disabled:opacity-50"
        >
          {isBootstrapping ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : 'Use Existing Trash'}
        </button>
      </div>
    </div>
  );
}

// Model Metrics Component
function ModelMetricsDisplay({ metrics }: { metrics: ModelMetrics | null }) {
  if (!metrics) {
    return (
      <div className="bg-blue-50 p-4 rounded border border-blue-200 text-center">
        <p className="text-blue-700">
          No model metrics available. Train a model to see performance statistics.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
      <h3 className="text-lg font-semibold mb-3">Model Performance Metrics</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="p-3 bg-indigo-50 rounded border border-indigo-100">
          <div className="text-xs text-indigo-600 font-medium">Accuracy</div>
          <div className="text-xl font-bold text-indigo-700">{metrics.accuracy !== undefined ? `${(metrics.accuracy * 100).toFixed(1)}%` : 'N/A'}</div>
        </div>
        <div className="p-3 bg-green-50 rounded border border-green-100">
          <div className="text-xs text-green-600 font-medium">Precision</div>
          <div className="text-xl font-bold text-green-700">{metrics.precision !== undefined ? `${(metrics.precision * 100).toFixed(1)}%` : 'N/A'}</div>
        </div>
        <div className="p-3 bg-blue-50 rounded border border-blue-100">
          <div className="text-xs text-blue-600 font-medium">Recall</div>
          <div className="text-xl font-bold text-blue-700">{metrics.recall !== undefined ? `${(metrics.recall * 100).toFixed(1)}%` : 'N/A'}</div>
        </div>
        <div className="p-3 bg-purple-50 rounded border border-purple-100">
          <div className="text-xs text-purple-600 font-medium">F1 Score</div>
          <div className="text-xl font-bold text-purple-700">{metrics.f1_score !== undefined ? `${(metrics.f1_score * 100).toFixed(1)}%` : 'N/A'}</div>
        </div>
      </div>
      
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Confusion Matrix</h4>
        {metrics.confusion_matrix ? (
          <div className="grid grid-cols-2 gap-2 max-w-xs">
            <div className="bg-green-100 p-2 rounded text-center border border-green-200">
              <div className="text-xs text-green-700">True Positive</div>
              <div className="font-bold">{metrics.confusion_matrix.true_positives}</div>
            </div>
            <div className="bg-red-100 p-2 rounded text-center border border-red-200">
              <div className="text-xs text-red-700">False Positive</div>
              <div className="font-bold">{metrics.confusion_matrix.false_positives}</div>
            </div>
            <div className="bg-red-100 p-2 rounded text-center border border-red-200">
              <div className="text-xs text-red-700">False Negative</div>
              <div className="font-bold">{metrics.confusion_matrix.false_negatives}</div>
            </div>
            <div className="bg-green-100 p-2 rounded text-center border border-green-200">
              <div className="text-xs text-green-700">True Negative</div>
              <div className="font-bold">{metrics.confusion_matrix.true_negatives}</div>
            </div>
          </div>
        ) : (
          <div className="bg-gray-50 p-3 rounded border border-gray-200 text-center">
            <p className="text-gray-500 text-sm">Confusion matrix data not available</p>
          </div>
        )}
      </div>
      
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Top Predictive Features</h4>
        {metrics.top_features && metrics.top_features.length > 0 ? (
          <div className="max-h-40 overflow-y-auto bg-gray-50 rounded p-2 border border-gray-200">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left text-gray-600">
                  <th className="py-1 px-2">Feature</th>
                  <th className="py-1 px-2">Class</th>
                  <th className="py-1 px-2">Importance</th>
                </tr>
              </thead>
              <tbody>
                {metrics.top_features.map((feature, index) => (
                  <tr key={index} className="border-t border-gray-200">
                    <td className="py-1 px-2 font-medium">{feature.feature}</td>
                    <td className="py-1 px-2">
                      <span className={`inline-block px-2 py-1 rounded-full text-xs ${
                        feature.class === 'trash' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                      }`}>
                        {feature.class}
                      </span>
                    </td>
                    <td className="py-1 px-2">{feature.importance.toFixed(3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="bg-gray-50 p-3 rounded border border-gray-200 text-center">
            <p className="text-gray-500 text-sm">Feature importance data not available</p>
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="bg-gray-50 p-2 rounded">
          <span className="text-gray-600">Training data size:</span>
          <span className="ml-2 font-medium">{metrics.training_size || 'N/A'} {metrics.training_size ? 'examples' : ''}</span>
        </div>
        <div className="bg-gray-50 p-2 rounded">
          <span className="text-gray-600">Test data size:</span>
          <span className="ml-2 font-medium">{metrics.test_size || 'N/A'} {metrics.test_size ? 'examples' : ''}</span>
        </div>
        <div className="bg-gray-50 p-2 rounded col-span-2">
          <span className="text-gray-600">Training time:</span>
          <span className="ml-2 font-medium">{metrics.training_time || 'N/A'}</span>
        </div>
      </div>
    </div>
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
  const [modelMetrics, setModelMetrics] = useState<ModelMetrics | null>(null);
  const [loadingMetrics, setLoadingMetrics] = useState(false);
  const [evaluatingModel, setEvaluatingModel] = useState(false);
  const [editingSenderId, setEditingSenderId] = useState<number | null>(null);
  const [newWeight, setNewWeight] = useState<number>(1);
  const [updating, setUpdating] = useState(false);

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

  useEffect(() => {
    // Fetch classifier status and metrics when the page loads
    fetchClassifierStatus();
    fetchModelMetrics();
  }, []);

  const fetchClassifierStatus = async () => {
    try {
      setLoadingClassifierStatus(true);
      const status = await getTrashClassifierStatus();
      setClassifierStatus(status);
      
      // If we have a trained model, also fetch metrics
      if (status.is_model_available) {
        fetchModelMetrics();
      }
    } catch (err) {
      console.error('Error fetching classifier status:', err);
    } finally {
      setLoadingClassifierStatus(false);
    }
  };

  const fetchModelMetrics = async () => {
    try {
      setLoadingMetrics(true);
      const metrics = await getClassifierMetrics();
      setModelMetrics(metrics);
    } catch (err) {
      console.error('Error fetching model metrics:', err);
      // Create a default metrics object with empty/null values
      // This ensures the UI can still render without errors
      setModelMetrics({
        accuracy: 0,
        precision: 0,
        recall: 0,
        f1_score: 0,
        confusion_matrix: {
          true_positives: 0,
          false_positives: 0,
          true_negatives: 0,
          false_negatives: 0
        },
        top_features: [],
        training_size: 0,
        test_size: 0,
        training_time: 'N/A'
      });
    } finally {
      setLoadingMetrics(false);
    }
  };

  const handleTrainClassifier = async (testSize: number) => {
    try {
      setTrainingClassifier(true);
      await trainTrashClassifier(testSize);
      
      // Show a notification
      alert('Trash classifier training has started. This may take a few moments.');
      
      // Poll for status updates
      const checkTrainingStatus = async () => {
        const status = await getTrashClassifierStatus();
        setClassifierStatus(status);
        
        if (status.is_model_available) {
          // Training completed, fetch metrics
          fetchModelMetrics();
          return true;
        }
        return false;
      };
      
      // Check status every 3 seconds for up to 30 seconds
      let attempts = 0;
      const maxAttempts = 10;
      const interval = setInterval(async () => {
        attempts++;
        const isComplete = await checkTrainingStatus();
        
        if (isComplete || attempts >= maxAttempts) {
          clearInterval(interval);
          setTrainingClassifier(false);
        }
      }, 3000);
    } catch (err) {
      console.error('Error training classifier:', err);
      alert('Failed to train classifier');
      setTrainingClassifier(false);
    }
  };

  const handleBootstrapData = async (testSize: number) => {
    try {
      setBootstrappingData(true);
      await bootstrapTrashClassifier(testSize);
      
      // Show a notification
      alert('Successfully prepared training data from your trash emails. Starting training process...');
      
      // Start training after bootstrap
      await handleTrainClassifier(testSize);
    } catch (err) {
      console.error('Error bootstrapping training data:', err);
      alert('Failed to prepare training data from trash');
      setBootstrappingData(false);
    }
  };

  const handleEvaluateModel = async () => {
    try {
      setEvaluatingModel(true);
      const metrics = await evaluateTrashClassifier();
      setModelMetrics(metrics);
      alert('Model evaluation completed successfully');
    } catch (err) {
      console.error('Error evaluating model:', err);
      alert('Failed to evaluate model');
    } finally {
      setEvaluatingModel(false);
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
      
      // Fetch rules for this category
      const keywords = await getCategoryKeywords(category.name);
      const senderRules = await getCategorySenderRules(category.name);
      
      // Identify system rules that have user overrides
      // Group sender rules by pattern to find duplicates (system + user override)
      const patternMap = new Map();
      senderRules.forEach(rule => {
        const key = `${rule.pattern}-${rule.is_domain}`;
        if (!patternMap.has(key)) {
          patternMap.set(key, []);
        }
        patternMap.get(key).push(rule);
      });
      
      // Mark overridden system rules
      const processedRules = senderRules.map(rule => {
        const key = `${rule.pattern}-${rule.is_domain}`;
        const rulesWithSamePattern = patternMap.get(key);
        // If there are multiple rules with this pattern and this is a system rule
        const isOverridden = rulesWithSamePattern.length > 1 && rule.user_id === null;
        return { ...rule, isOverridden };
      });
      
      setSelectedCategoryKeywords(keywords);
      setSelectedCategorySenderRules(processedRules);
      setIsViewRulesModalOpen(true);
    } catch (error) {
      console.error("Error fetching category details:", error);
      toast.error(error instanceof Error ? error.message : "Failed to fetch category details");
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

  const handleUpdateSenderRuleWeight = async (ruleId: number, weight: number) => {
    try {
      setUpdating(true);
      await updateSenderRuleWeight(ruleId, weight);
      
      // Refresh the rules for this category
      if (selectedCategory) {
        const updatedRules = await getCategorySenderRules(selectedCategory.name);
        setSelectedCategorySenderRules(updatedRules);
      }
      
      setEditingSenderId(null);
      toast.success("Sender rule weight has been updated successfully. New emails will be categorized using this weight.");
    } catch (error) {
      console.error("Error updating sender rule:", error);
      toast.error(error instanceof Error ? error.message : "Failed to update sender rule");
    } finally {
      setUpdating(false);
    }
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

      {/* ML Classifier Section */}
      <div className="mb-8 bg-white rounded-lg shadow-md p-6 border border-gray-200">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
          <div>
            <h2 className="text-xl font-semibold flex items-center mb-2">
              <BeakerIcon className="h-6 w-6 mr-2 text-purple-600" />
              ML Trash Classifier
            </h2>
            <p className="text-gray-600">
              Train a model to automatically identify unwanted emails based on your preferences
            </p>
          </div>
          
          {classifierStatus?.is_model_available && (
            <button
              onClick={handleEvaluateModel}
              disabled={evaluatingModel}
              className="mt-4 md:mt-0 bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded flex items-center"
            >
              {evaluatingModel ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Evaluating...
                </>
              ) : 'Evaluate Model'}
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            {loadingClassifierStatus ? (
              <div className="flex justify-center py-6">
                <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-purple-500"></div>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Training status panel */}
                <div className="bg-gray-50 p-4 rounded border border-gray-200">
                  <h3 className="font-medium text-gray-800 mb-2">Training Status</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-500">Status</div>
                      <div className={`font-medium ${classifierStatus?.is_model_available ? 'text-green-600' : 'text-amber-600'}`}>
                        {classifierStatus?.is_model_available ? 'Model Active' : 'Not Available'}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Training Data</div>
                      <div className="font-medium">
                        {classifierStatus?.trash_events_count || 0} / {classifierStatus?.recommended_min_events || 10} events
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div className="bg-purple-600 h-2 rounded-full" style={{ 
                          width: `${Math.min(100, ((classifierStatus?.trash_events_count || 0) / (classifierStatus?.recommended_min_events || 10)) * 100)}%` 
                        }}></div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Training configuration */}
                <MLClassifierConfig 
                  onTrain={handleTrainClassifier}
                  onBootstrap={handleBootstrapData}
                  classifierStatus={classifierStatus}
                  isTraining={trainingClassifier}
                  isBootstrapping={bootstrappingData}
                />
                
                {/* Model improvement tips */}
                <div className="bg-yellow-50 p-4 rounded border border-yellow-200 text-sm">
                  <h3 className="font-medium text-yellow-800 mb-2">Tips to Improve Model Performance</h3>
                  <ul className="list-disc list-inside space-y-1 text-yellow-700">
                    <li>Add more examples by moving emails to trash</li>
                    <li>Ensure your trash contains diverse example types</li>
                    <li>Remove ambiguous examples from trash</li>
                    <li>Reprocess your emails after training</li>
                    <li>Add more distinctive keywords to categories</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
          
          <div>
            {loadingMetrics ? (
              <div className="flex justify-center py-6">
                <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-purple-500"></div>
              </div>
            ) : (
              <ModelMetricsDisplay metrics={modelMetrics} />
            )}
          </div>
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
                      
                      {selectedCategory?.name === 'newsletters' && (
                        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-4 rounded">
                          <p className="text-sm text-blue-800">
                            <strong>Tip:</strong> Increasing the weight of sender rules for newsletters can help ensure they don't 
                            get incorrectly categorized as Important. For domains you always want in Newsletters, try setting a weight of 3 or higher.
                          </p>
                          <p className="text-sm text-blue-800 mt-2">
                            <strong>Note:</strong> Existing emails may need to be reprocessed to apply new weights. 
                            Press the "Reprocess All Emails" button after making changes.
                          </p>
                        </div>
                      )}
                      
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
                                    
                                    {editingSenderId === rule.id ? (
                                      <div className="flex items-center space-x-2">
                                        <input 
                                          type="number" 
                                          min="1" 
                                          max="10"
                                          className="w-16 px-2 py-1 border rounded"
                                          value={newWeight}
                                          onChange={(e) => setNewWeight(parseInt(e.target.value))}
                                        />
                                        <button
                                          onClick={() => handleUpdateSenderRuleWeight(rule.id, newWeight)}
                                          disabled={updating}
                                          className="px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                                        >
                                          Save
                                        </button>
                                        <button
                                          onClick={() => setEditingSenderId(null)}
                                          className="px-2 py-1 bg-gray-300 text-gray-800 rounded hover:bg-gray-400"
                                        >
                                          Cancel
                                        </button>
                                      </div>
                                    ) : (
                                      <>
                                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                                          Weight: {rule.weight}
                                        </span>
                                        <button
                                          onClick={() => {
                                            setEditingSenderId(rule.id);
                                            setNewWeight(rule.weight);
                                          }}
                                          className="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                                        >
                                          Edit
                                        </button>
                                      </>
                                    )}
                                    
                                    {rule.user_id ? (
                                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded">User</span>
                                    ) : (
                                      <span className={`px-2 py-1 rounded ${rule.isOverridden ? 'bg-yellow-100 text-yellow-800' : 'bg-purple-100 text-purple-800'}`}>
                                        {rule.isOverridden ? 'Overridden' : 'System'}
                                      </span>
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