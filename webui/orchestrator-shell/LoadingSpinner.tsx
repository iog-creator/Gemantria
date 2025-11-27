import React from 'react';

interface LoadingSpinnerProps {
  message?: string;
}

export default function LoadingSpinner({ message = 'Loading...' }: LoadingSpinnerProps) {
  return (
    <div className="p-8 text-center">
      <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-blue-200 border-t-blue-600 mb-4"></div>
      <p className="text-gray-500">{message}</p>
    </div>
  );
}

