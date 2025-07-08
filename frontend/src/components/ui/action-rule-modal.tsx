'use client';

import { useState, useEffect } from 'react';
import { ActionRule, ActionRuleRequest, getActionPreview } from '@/lib/api';

interface ActionRuleModalProps {
  isOpen: boolean;
  onClose: () => void;
  categoryId: number;
  categoryName: string;
  initialRule?: ActionRule;
  onSave: (rule: ActionRuleRequest) => Promise<void>;
}

export function ActionRuleModal({
  isOpen,
  onClose,
  categoryId,
  categoryName,
  initialRule,
  onSave,
}: ActionRuleModalProps) {
  const [formData, setFormData] = useState<ActionRuleRequest>({
    action: 'ARCHIVE',
    delay_days: 7,
    enabled: true,
  });
  const [preview, setPreview] = useState<{
    affected_email_count: number;
    affected_emails: Array<{
      id: string;
      subject: string;
      from_email: string;
      received_at: string;
      age_days: number;
    }>;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (isOpen && initialRule) {
      setFormData({
        action: initialRule.action || 'ARCHIVE',
        delay_days: initialRule.delay_days || 7,
        enabled: initialRule.enabled,
      });
    } else if (isOpen) {
      setFormData({
        action: 'ARCHIVE',
        delay_days: 7,
        enabled: true,
      });
    }
  }, [isOpen, initialRule]);

  useEffect(() => {
    if (isOpen && formData.action && formData.delay_days) {
      loadPreview();
    }
  }, [isOpen, formData.action, formData.delay_days]);

  const loadPreview = async () => {
    if (!formData.action || !formData.delay_days) return;
    
    setPreviewLoading(true);
    try {
      const previewData = await getActionPreview(categoryId);
      setPreview(previewData);
    } catch (error) {
      console.error('Failed to load preview:', error);
      setPreview(null);
    } finally {
      setPreviewLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.action) {
      newErrors.action = 'Please select an action type';
    }

    if (!formData.delay_days || formData.delay_days < 1) {
      newErrors.delay_days = 'Delay must be at least 1 day';
    }

    if (formData.delay_days > 365) {
      newErrors.delay_days = 'Delay cannot exceed 365 days';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    try {
      await onSave(formData);
      onClose();
    } catch (error) {
      console.error('Failed to save action rule:', error);
      setErrors({ submit: 'Failed to save action rule. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const getActionDescription = (action: string) => {
    switch (action) {
      case 'ARCHIVE':
        return 'Move emails to archive folder';
      case 'TRASH':
        return 'Move emails to trash folder';
      default:
        return '';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              Configure Action Rule - {categoryName}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 focus:outline-none"
            >
              <span className="sr-only">Close</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Action Type Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Action Type</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label className="relative">
                <input
                  type="radio"
                  name="action"
                  value="ARCHIVE"
                  checked={formData.action === 'ARCHIVE'}
                  onChange={(e) => setFormData({ ...formData, action: e.target.value as 'ARCHIVE' | 'TRASH' })}
                  className="sr-only"
                />
                <div className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  formData.action === 'ARCHIVE'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}>
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">📤</span>
                    <div>
                      <div className="font-medium">Archive</div>
                      <div className="text-sm text-gray-500">Move emails to archive folder</div>
                    </div>
                  </div>
                </div>
              </label>

              <label className="relative">
                <input
                  type="radio"
                  name="action"
                  value="TRASH"
                  checked={formData.action === 'TRASH'}
                  onChange={(e) => setFormData({ ...formData, action: e.target.value as 'ARCHIVE' | 'TRASH' })}
                  className="sr-only"
                />
                <div className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  formData.action === 'TRASH'
                    ? 'border-red-500 bg-red-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}>
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">🗑️</span>
                    <div>
                      <div className="font-medium">Trash</div>
                      <div className="text-sm text-gray-500">Move emails to trash folder</div>
                    </div>
                  </div>
                </div>
              </label>
            </div>
            {errors.action && (
              <p className="text-red-600 text-sm">{errors.action}</p>
            )}
          </div>

          {/* Timing Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Timing</h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center space-x-3">
                <label htmlFor="delay_days" className="text-sm font-medium text-gray-700">
                  Wait for:
                </label>
                <input
                  id="delay_days"
                  type="number"
                  min="1"
                  max="365"
                  value={formData.delay_days}
                  onChange={(e) => setFormData({ ...formData, delay_days: parseInt(e.target.value) || 0 })}
                  className="w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                />
                <span className="text-sm text-gray-700">days after email is received</span>
              </div>
              {errors.delay_days && (
                <p className="text-red-600 text-sm mt-2">{errors.delay_days}</p>
              )}
            </div>
          </div>

          {/* Preview Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Preview</h3>
            <div className="bg-gray-50 p-4 rounded-lg">
              {previewLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
                  <span className="text-sm text-gray-600">Loading preview...</span>
                </div>
              ) : preview ? (
                <div className="space-y-3">
                  <div className="text-sm">
                    <span className="font-medium">
                      {preview.affected_email_count} emails will be affected by this rule
                    </span>
                  </div>
                  
                  {preview.affected_emails.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-sm font-medium text-gray-700">Sample emails:</div>
                      {preview.affected_emails.slice(0, 3).map((email) => (
                        <div key={email.id} className="text-sm text-gray-600 bg-white p-2 rounded border">
                          <div className="font-medium">{email.subject}</div>
                          <div className="text-xs text-gray-500">
                            From: {email.from_email} • {email.age_days} days old
                          </div>
                        </div>
                      ))}
                      {preview.affected_emails.length > 3 && (
                        <div className="text-sm text-gray-500">
                          ... and {preview.affected_emails.length - 3} more
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-sm text-gray-500">
                  No emails would be affected by this rule.
                </div>
              )}
            </div>
          </div>

          {/* Safety Settings Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Safety Settings</h3>
            <div className="bg-gray-50 p-4 rounded-lg space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.enabled}
                  onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Enable this action rule immediately
                </span>
              </label>
              
              <div className="text-sm text-gray-500">
                <p>💡 You can always disable this rule later if needed.</p>
                <p>💡 The system will show you proposed actions before executing them.</p>
              </div>
            </div>
          </div>

          {/* Error Display */}
          {errors.submit && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-red-600 text-sm">{errors.submit}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Saving...' : initialRule ? 'Update Rule' : 'Create Rule'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 