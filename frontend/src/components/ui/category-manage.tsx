import { useState } from 'react';
import { Category, SenderRule, CategoryKeyword, updateSenderRuleWeight, deleteCategory, deleteSenderRule, deleteKeyword, updateKeywordWeight, updateSenderRulePattern } from '@/lib/api';
import { toast } from 'react-hot-toast';
import { TrashIcon, PencilIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface CategoryManageProps {
  category: Category;
  senderRules: SenderRule[];
  keywords: CategoryKeyword[];
  onDelete: () => void;
  onRefresh: () => void;
}

export function CategoryManage({ 
  category, 
  senderRules, 
  keywords, 
  onDelete,
  onRefresh 
}: CategoryManageProps) {
  const [editingSenderId, setEditingSenderId] = useState<number | null>(null);
  const [editingKeywordId, setEditingKeywordId] = useState<number | null>(null);
  const [editingSenderPatternId, setEditingSenderPatternId] = useState<number | null>(null);
  const [newWeight, setNewWeight] = useState<number>(1);
  const [newKeywordWeight, setNewKeywordWeight] = useState<number>(1);
  const [newPattern, setNewPattern] = useState<string>('');
  const [newIsDomain, setNewIsDomain] = useState<boolean>(true);
  const [updating, setUpdating] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingSenderId, setDeletingSenderId] = useState<number | null>(null);
  const [deletingKeywordId, setDeletingKeywordId] = useState<number | null>(null);
  const [patternError, setPatternError] = useState<string | null>(null);

  const handleUpdateSenderRuleWeight = async (ruleId: number, weight: number) => {
    try {
      setUpdating(true);
      const updatedRule = await updateSenderRuleWeight(ruleId, weight);
      
      // Determine if this was an in-place update or a new override rule
      const isNewRule = updatedRule.id !== ruleId;
      if (isNewRule) {
        toast.success("A new override rule has been created with the updated weight.");
      } else {
        toast.success("Sender rule weight has been updated successfully.");
      }
      
      // After updating a rule weight, refresh the entire list 
      await onRefresh();
      
      setEditingSenderId(null);
    } catch (error) {
      console.error("Error updating sender rule:", error);
      toast.error(error instanceof Error ? error.message : "Failed to update sender rule");
    } finally {
      setUpdating(false);
    }
  };

  const handleUpdateSenderRulePattern = async (ruleId: number, pattern: string, isDomain: boolean) => {
    try {
      setUpdating(true);
      setPatternError(null);
      const updatedRule = await updateSenderRulePattern(ruleId, pattern, isDomain);
      const isNewRule = updatedRule.id !== ruleId;
      if (isNewRule) {
        toast.success("A new override rule has been created with the updated pattern.");
      } else {
        toast.success("Sender rule pattern has been updated successfully.");
      }
      await onRefresh();
      setEditingSenderPatternId(null);
    } catch (error: any) {
      console.error("Error updating sender rule pattern:", error);
      // Support FastAPI error format: error.message is string, but error.response?.detail may be object
      let categoryDisplayName = '';
      let detail = '';
      let message = '';
      if (error && error.response && error.response.detail) {
        // If detail is an object (FastAPI custom error)
        if (typeof error.response.detail === 'object') {
          message = error.response.detail.message || '';
          categoryDisplayName = error.response.detail.category_display_name || '';
        } else {
          // If detail is a string
          message = error.response.detail;
        }
      } else if (error && error.message) {
        // Fallback: try to parse JSON from error.message if possible
        try {
          const parsed = JSON.parse(error.message);
          message = parsed.message || parsed.detail || '';
          categoryDisplayName = parsed.category_display_name || '';
        } catch {
          message = error.message;
        }
      }
      if (categoryDisplayName) {
        setPatternError(
          `A sender rule for this domain or pattern already exists in the "${categoryDisplayName}" category. Please edit or remove it there, or choose a different value.`
        );
      } else if (message && (message.includes('already exists') || message.includes('unique constraint'))) {
        setPatternError(
          'A sender rule for this domain or pattern already exists. Please choose a different value or edit the existing rule.'
        );
      } else {
        setPatternError('Failed to update sender rule pattern. Please try again.');
      }
      toast.error(message || 'Failed to update sender rule pattern');
    } finally {
      setUpdating(false);
    }
  };

  const handleUpdateKeywordWeight = async (keywordId: number, weight: number) => {
    try {
      setUpdating(true);
      const updatedKeyword = await updateKeywordWeight(keywordId, weight);
      
      // Determine if this was an in-place update or a new override keyword
      const isNewKeyword = updatedKeyword.id !== keywordId;
      if (isNewKeyword) {
        toast.success("A new override keyword has been created with the updated weight.");
      } else {
        toast.success("Keyword weight has been updated successfully.");
      }
      
      // After updating a keyword weight, refresh the entire list
      await onRefresh();
      
      setEditingKeywordId(null);
    } catch (error) {
      console.error("Error updating keyword:", error);
      toast.error(error instanceof Error ? error.message : "Failed to update keyword");
    } finally {
      setUpdating(false);
    }
  };

  const handleDeleteCategory = async () => {
    if (category.is_system) {
      toast.error("System categories cannot be deleted");
      return;
    }
    
    try {
      await deleteCategory(category.name);
      toast.success(`Category "${category.display_name}" has been deleted`);
      onDelete();
    } catch (error) {
      console.error("Error deleting category:", error);
      toast.error(error instanceof Error ? error.message : "Failed to delete category");
    } finally {
      setShowDeleteConfirm(false);
    }
  };

  const handleDeleteSenderRule = async (ruleId: number) => {
    try {
      setUpdating(true);
      await deleteSenderRule(ruleId);
      toast.success("Sender rule has been deleted successfully.");
      await onRefresh();
      setDeletingSenderId(null);
    } catch (error) {
      console.error("Error deleting sender rule:", error);
      toast.error(error instanceof Error ? error.message : "Failed to delete sender rule");
    } finally {
      setUpdating(false);
    }
  };

  const handleDeleteKeyword = async (keywordId: number) => {
    try {
      setUpdating(true);
      await deleteKeyword(keywordId);
      toast.success("Keyword has been deleted successfully.");
      await onRefresh();
      setDeletingKeywordId(null);
    } catch (error) {
      console.error("Error deleting keyword:", error);
      // Check if the error is a 403 Forbidden related to system keywords
      if (error instanceof Error && error.message.includes('403')) {
        toast.error("You can only delete your own keywords. System keywords cannot be deleted.");
      } else {
        toast.error(error instanceof Error ? error.message : "Failed to delete keyword");
      }
      setDeletingKeywordId(null);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-semibold">{category.display_name}</h3>
          <p className="text-gray-600 text-sm">{category.description}</p>
          <div className="flex space-x-2 mt-2">
            <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
              Priority: {category.priority}
            </span>
            <span className={`px-2 py-1 ${category.is_system ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'} rounded text-xs`}>
              {category.is_system ? 'System' : 'User'}
            </span>
          </div>
        </div>
        
        {!category.is_system && (
          <div>
            {showDeleteConfirm ? (
              <div className="flex flex-col space-y-2">
                <p className="text-red-600 text-sm font-medium">Are you sure?</p>
                <div className="flex space-x-2">
                  <button 
                    onClick={handleDeleteCategory}
                    className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
                  >
                    Yes, Delete
                  </button>
                  <button 
                    onClick={() => setShowDeleteConfirm(false)}
                    className="px-3 py-1 bg-gray-200 text-gray-800 rounded text-sm hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button 
                onClick={() => setShowDeleteConfirm(true)}
                className="px-3 py-1 bg-red-100 text-red-600 rounded hover:bg-red-200"
              >
                Delete
              </button>
            )}
          </div>
        )}
      </div>

      <div className="mt-6">
        <h4 className="text-lg font-medium mb-3">
          Keywords ({keywords.length})
        </h4>
        
        {keywords.length > 0 ? (
          <ul className="border rounded-md divide-y">
            {keywords.map((keyword) => (
              <li key={keyword.id} className="p-3">
                <div className="flex justify-between items-center">
                  <div>
                    <span className="font-medium">{keyword.keyword}</span>
                    {keyword.is_regex && (
                      <span className="ml-2 text-gray-500 text-sm">(regex)</span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    {editingKeywordId === keyword.id ? (
                      <div className="flex items-center space-x-2">
                        <input 
                          type="number" 
                          min="1" 
                          max="10"
                          className="w-16 px-2 py-1 border rounded"
                          value={newKeywordWeight}
                          onChange={(e) => setNewKeywordWeight(parseInt(e.target.value))}
                        />
                        <button
                          onClick={() => handleUpdateKeywordWeight(keyword.id, newKeywordWeight)}
                          disabled={updating}
                          className="p-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setEditingKeywordId(null)}
                          className="p-1 bg-gray-300 text-gray-800 rounded hover:bg-gray-400"
                        >
                          <XMarkIcon className="h-4 w-4" />
                        </button>
                      </div>
                    ) : (
                      <>
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                          Weight: {keyword.weight}
                        </span>
                        <button
                          onClick={() => {
                            setEditingKeywordId(keyword.id);
                            setNewKeywordWeight(keyword.weight);
                          }}
                          className="p-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                          title={keyword.user_id ? "Edit weight" : "Create user override with custom weight"}
                        >
                          <PencilIcon className="h-4 w-4" />
                        </button>
                      </>
                    )}
                    
                    {deletingKeywordId === keyword.id ? (
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-red-600">Delete?</span>
                        <button
                          onClick={() => handleDeleteKeyword(keyword.id)}
                          disabled={updating}
                          className="p-1 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                        >
                          Yes
                        </button>
                        <button
                          onClick={() => setDeletingKeywordId(null)}
                          className="p-1 bg-gray-300 text-gray-800 rounded hover:bg-gray-400"
                        >
                          No
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setDeletingKeywordId(keyword.id)}
                        className={`p-1 ${keyword.user_id ? 'bg-red-100 text-red-600 hover:bg-red-200' : 'bg-gray-100 text-gray-400 cursor-not-allowed'} rounded`}
                        title={keyword.user_id ? "Delete keyword" : "System keywords cannot be deleted"}
                        disabled={!keyword.user_id}
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    )}
                    
                    <span className={`px-2 py-1 rounded text-xs flex items-center ${keyword.user_id ? 'bg-green-100 text-green-800' : 'bg-purple-100 text-purple-800'}`}>
                      {keyword.user_id ? 'User' : (
                        <span className="flex items-center">
                          System
                          <span className="ml-1 text-xs text-purple-600 cursor-help" title="System keywords cannot be deleted, but you can create user overrides with custom weights">
                            ⓘ
                          </span>
                        </span>
                      )}
                    </span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 italic">No keywords defined</p>
        )}
      </div>

      <div className="mt-6">
        <h4 className="text-lg font-medium mb-3">
          Sender Rules ({senderRules.length})
        </h4>

        {category.name === 'newsletters' && (
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
        
        {senderRules.length > 0 ? (
          <ul className="border rounded-md divide-y">
            {senderRules.map((rule) => (
              <li key={rule.id} className="p-3">
                {editingSenderPatternId === rule.id ? (
                  <div className="mb-3">
                    {/* Error message for pattern update */}
                    {patternError && (
                      <div className="mb-2 p-3 bg-red-100 border border-red-400 text-red-700 rounded flex items-start justify-between">
                        <span>
                          <strong>Error:</strong> {patternError}
                        </span>
                        <button
                          onClick={() => setPatternError(null)}
                          className="ml-4 text-red-700 hover:text-red-900 font-bold"
                          aria-label="Dismiss error"
                        >
                          ×
                        </button>
                      </div>
                    )}
                    <div className="flex items-center space-x-2 mb-2">
                      <input 
                        type="text"
                        className="flex-1 px-2 py-1 border rounded"
                        value={newPattern}
                        onChange={(e) => setNewPattern(e.target.value)}
                        placeholder={newIsDomain ? "example.com" : "@example.com"}
                      />
                      <div className="flex items-center">
                        <input
                          id={`isDomain-${rule.id}`}
                          type="checkbox"
                          checked={newIsDomain}
                          onChange={(e) => setNewIsDomain(e.target.checked)}
                          className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                        />
                        <label htmlFor={`isDomain-${rule.id}`} className="ml-2 text-sm text-gray-700">
                          Is domain
                        </label>
                      </div>
                    </div>
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => handleUpdateSenderRulePattern(rule.id, newPattern, newIsDomain)}
                        disabled={updating || !newPattern.trim()}
                        className="px-2 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 text-xs"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => { setEditingSenderPatternId(null); setPatternError(null); }}
                        className="px-2 py-1 bg-gray-300 text-gray-800 rounded hover:bg-gray-400 text-xs"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex justify-between items-center">
                    <div>
                      <span className="font-medium">{rule.pattern}</span>
                      <span className="ml-2 text-gray-500 text-sm">
                        {rule.is_domain ? '(domain)' : '(substring)'}
                      </span>
                      <button
                        onClick={() => {
                          setEditingSenderPatternId(rule.id);
                          setNewPattern(rule.pattern);
                          setNewIsDomain(rule.is_domain);
                        }}
                        className="ml-2 p-1 bg-indigo-100 text-indigo-600 rounded hover:bg-indigo-200 text-xs"
                        title="Edit pattern"
                      >
                        Edit
                      </button>
                    </div>
                    <div className="flex items-center space-x-2">
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
                            className="p-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingSenderId(null)}
                            className="p-1 bg-gray-300 text-gray-800 rounded hover:bg-gray-400"
                          >
                            <XMarkIcon className="h-4 w-4" />
                          </button>
                        </div>
                      ) : (
                        <>
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                            Weight: {rule.weight}
                          </span>
                          <button
                            onClick={() => {
                              setEditingSenderId(rule.id);
                              setNewWeight(rule.weight);
                            }}
                            className="p-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                            title="Edit weight"
                          >
                            <PencilIcon className="h-4 w-4" />
                          </button>
                        </>
                      )}
                      
                      {deletingSenderId === rule.id ? (
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-red-600">Delete?</span>
                          <button
                            onClick={() => handleDeleteSenderRule(rule.id)}
                            disabled={updating}
                            className="p-1 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                          >
                            Yes
                          </button>
                          <button
                            onClick={() => setDeletingSenderId(null)}
                            className="p-1 bg-gray-300 text-gray-800 rounded hover:bg-gray-400"
                          >
                            No
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setDeletingSenderId(rule.id)}
                          className="p-1 bg-red-100 text-red-600 rounded hover:bg-red-200"
                          title="Delete sender rule"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      )}
                      
                      <span className={`px-2 py-1 rounded text-xs ${
                        rule.user_id ? 'bg-green-100 text-green-800' : 'bg-purple-100 text-purple-800'
                      }`}>
                        {rule.user_id ? 'User' : 'System'}
                      </span>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 italic">No sender rules defined</p>
        )}
      </div>
    </div>
  );
} 