'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { 
  ActionRule, 
  ActionRuleRequest, 
  getActionRules, 
  createActionRule, 
  updateActionRule, 
  deleteActionRule, 
  toggleActionRule 
} from '@/lib/api';
import { toast } from 'react-hot-toast';

interface ActionEngineContextType {
  actionRules: Record<number, ActionRule[]>;
  loading: boolean;
  error: string | null;
  refreshRules: (categoryId?: number) => Promise<void>;
  updateRule: (categoryId: number, rule: ActionRuleRequest) => Promise<void>;
  createRule: (categoryId: number, rule: ActionRuleRequest) => Promise<void>;
  deleteRule: (categoryId: number) => Promise<void>;
  toggleRule: (categoryId: number, enabled: boolean) => Promise<void>;
  getRulesForCategory: (categoryId: number) => ActionRule[];
}

const ActionEngineContext = createContext<ActionEngineContextType | undefined>(undefined);

interface ActionEngineProviderProps {
  children: ReactNode;
}

export function ActionEngineProvider({ children }: ActionEngineProviderProps) {
  const [actionRules, setActionRules] = useState<Record<number, ActionRule[]>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshRules = async (categoryId?: number) => {
    console.log('🔄 Refreshing action rules for category:', categoryId || 'all');
    setLoading(true);
    setError(null);
    
    try {
      if (categoryId) {
        // Refresh rules for a specific category
        const rules = await getActionRules(categoryId);
        console.log('📋 Loaded rules for category', categoryId, ':', rules);
        setActionRules(prev => ({
          ...prev,
          [categoryId]: rules
        }));
      } else {
        // Refresh all rules
        const allRules = await getActionRules();
        console.log('📋 Loaded all action rules:', allRules);
        const rulesByCategory: Record<number, ActionRule[]> = {};
        
        allRules.forEach(rule => {
          if (!rulesByCategory[rule.category_id]) {
            rulesByCategory[rule.category_id] = [];
          }
          rulesByCategory[rule.category_id].push(rule);
        });
        
        setActionRules(rulesByCategory);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to refresh action rules';
      setError(errorMessage);
      console.error('Error refreshing action rules:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateRule = async (categoryId: number, rule: ActionRuleRequest) => {
    try {
      await updateActionRule(categoryId, rule);
      await refreshRules(categoryId);
      toast.success('Action rule updated successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update action rule';
      toast.error(errorMessage);
      throw err;
    }
  };

  const createRule = async (categoryId: number, rule: ActionRuleRequest) => {
    try {
      await createActionRule(categoryId, rule);
      await refreshRules(categoryId);
      toast.success('Action rule created successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create action rule';
      toast.error(errorMessage);
      throw err;
    }
  };

  const deleteRule = async (categoryId: number) => {
    try {
      await deleteActionRule(categoryId);
      await refreshRules(categoryId);
      toast.success('Action rule deleted successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete action rule';
      toast.error(errorMessage);
      throw err;
    }
  };

  const toggleRule = async (categoryId: number, enabled: boolean) => {
    try {
      await toggleActionRule(categoryId, enabled);
      await refreshRules(categoryId);
      toast.success(`Action rule ${enabled ? 'enabled' : 'disabled'} successfully`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to toggle action rule';
      toast.error(errorMessage);
      throw err;
    }
  };

  const getRulesForCategory = (categoryId: number): ActionRule[] => {
    return actionRules[categoryId] || [];
  };

  // Initial load of action rules
  useEffect(() => {
    refreshRules();
  }, []);

  const value: ActionEngineContextType = {
    actionRules,
    loading,
    error,
    refreshRules,
    updateRule,
    createRule,
    deleteRule,
    toggleRule,
    getRulesForCategory,
  };

  return (
    <ActionEngineContext.Provider value={value}>
      {children}
    </ActionEngineContext.Provider>
  );
}

export function useActionEngine() {
  const context = useContext(ActionEngineContext);
  if (context === undefined) {
    throw new Error('useActionEngine must be used within an ActionEngineProvider');
  }
  return context;
} 