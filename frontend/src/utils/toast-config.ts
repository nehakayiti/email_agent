// Toast configuration settings for consistent behavior across the application

import { toast, ToastOptions } from 'react-hot-toast';

// Extended duration for toasts (6 seconds instead of default 3)
export const defaultToastOptions: ToastOptions = {
  duration: 6000, // 6 seconds
  position: 'top-right',
};

// Wrapper functions to ensure consistent toast behavior
export const showSuccessToast = (message: string, options?: ToastOptions) => {
  return toast.success(message, { ...defaultToastOptions, ...options });
};

export const showErrorToast = (message: string, options?: ToastOptions) => {
  return toast.error(message, { ...defaultToastOptions, ...options });
};

export const showLoadingToast = (message: string, options?: ToastOptions) => {
  return toast.loading(message, { ...defaultToastOptions, ...options });
};

// Utility to dismiss all toasts
export const dismissAllToasts = () => {
  toast.dismiss();
}; 