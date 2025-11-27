import React from 'react';

interface StatusBannerProps {
  mode: 'hermetic' | 'live' | 'error';
  message?: string;
  onDismiss?: () => void;
}

export default function StatusBanner({ mode, message, onDismiss }: StatusBannerProps) {
  const styles = {
    hermetic: 'bg-blue-50 border-blue-200 text-blue-800',
    live: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  };

  const icons = {
    hermetic: '📦',
    live: '🟢',
    error: '⚠️',
  };

  return (
    <div className={`mb-4 p-3 border rounded text-sm ${styles[mode]}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span>{icons[mode]}</span>
          <span className="font-medium">
            {mode === 'hermetic' && 'Static Mode'}
            {mode === 'live' && 'Live Search'}
            {mode === 'error' && 'Error'}
          </span>
          {message && <span className="ml-2">{message}</span>}
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-gray-500 hover:text-gray-700 ml-4"
            aria-label="Dismiss"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}

