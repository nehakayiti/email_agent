'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Category, getCategoriesApi } from './api';

interface CategoryContextType {
  categories: Category[];
  loading: boolean;
  error: string | null;
  refreshCategories: () => void;
  getCategoryInfo: (categoryName: string) => { 
    display_name: string;
    color: string;
    description: string | null;
  } | null;
}

const defaultCategoryContext: CategoryContextType = {
  categories: [],
  loading: true,
  error: null,
  refreshCategories: () => {},
  getCategoryInfo: () => null,
};

const CategoryContext = createContext<CategoryContextType>(defaultCategoryContext);

export function useCategoryContext() {
  return useContext(CategoryContext);
}

export function CategoryProvider({ children }: { children: ReactNode }) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    async function fetchCategories() {
      try {
        setLoading(true);
        const response = await getCategoriesApi();
        // Sort categories by priority (lower number = higher priority)
        const sortedCategories = response.data.sort((a, b) => a.priority - b.priority);
        setCategories(sortedCategories);
        setError(null);
      } catch (error) {
        console.error('Error fetching categories:', error);
        setError('Failed to load categories');
      } finally {
        setLoading(false);
      }
    }
    
    fetchCategories();
  }, [refreshKey]);

  // Helper function to get category display information
  const getCategoryInfo = (categoryName: string) => {
    if (!categoryName) return null;
    
    // Normalize category name to match API format
    const normalizedName = categoryName.toUpperCase().startsWith('CATEGORY_') 
      ? categoryName.toUpperCase() 
      : `CATEGORY_${categoryName.toUpperCase()}`;
    
    // Special case for primary/inbox which doesn't follow the CATEGORY_ pattern
    const searchName = normalizedName === 'CATEGORY_PRIMARY' ? 'PRIMARY' : normalizedName;
    
    // Find the category in our list
    const category = categories.find(c => 
      c.name.toUpperCase() === searchName || 
      c.name.toUpperCase() === categoryName.toUpperCase()
    );
    
    if (!category) {
      // Default styles if category not found
      const defaultStyles: Record<string, { display_name: string, color: string, description: string | null }> = {
        'PRIMARY': { 
          display_name: 'Primary', 
          color: 'bg-blue-100 text-blue-800 border border-blue-200',
          description: null
        },
        'TRASH': { 
          display_name: 'Trash', 
          color: 'bg-red-100 text-red-800 border border-red-200',
          description: null
        },
        'ARCHIVE': { 
          display_name: 'Archive', 
          color: 'bg-gray-100 text-gray-800 border border-gray-200',
          description: null
        }
      };
      
      return defaultStyles[categoryName.toUpperCase()] || null;
    }
    
    // Map category name to tailwind classes for styling
    // We could store these colors in the database as well
    const colorMap: Record<string, string> = {
      'CATEGORY_PERSONAL': 'bg-indigo-100 text-indigo-800 border border-indigo-200',
      'CATEGORY_UPDATES': 'bg-purple-100 text-purple-800 border border-purple-200',
      'CATEGORY_SOCIAL': 'bg-green-100 text-green-800 border border-green-200',
      'CATEGORY_PROMOTIONS': 'bg-orange-100 text-orange-800 border border-orange-200',
      'CATEGORY_FORUMS': 'bg-teal-100 text-teal-800 border border-teal-200',
      'PRIMARY': 'bg-blue-100 text-blue-800 border border-blue-200',
      // Defaults for other categories
      'default': 'bg-gray-100 text-gray-800 border border-gray-200'
    };
    
    return {
      display_name: category.display_name,
      color: colorMap[category.name] || colorMap.default,
      description: category.description
    };
  };

  const refreshCategories = () => {
    setRefreshKey(prev => prev + 1);
  };

  const value = {
    categories,
    loading,
    error,
    refreshCategories,
    getCategoryInfo
  };

  return (
    <CategoryContext.Provider value={value}>
      {children}
    </CategoryContext.Provider>
  );
} 