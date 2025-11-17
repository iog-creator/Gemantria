// PLAN-081: Browser-Verified Badge — shows browser verification status
import React, { useEffect, useState } from 'react';
import { fetchBrowserVerificationStatus, BrowserVerificationStatus } from '../api';

interface BrowserVerifiedBadgeProps {
  status?: BrowserVerificationStatus | null;
  className?: string;
}

const BrowserVerifiedBadge: React.FC<BrowserVerifiedBadgeProps> = ({
  status: propStatus,
  className = '',
}) => {
  const [status, setStatus] = useState<BrowserVerificationStatus | null>(propStatus || null);
  const [loading, setLoading] = useState(!propStatus);

  useEffect(() => {
    if (propStatus !== undefined) {
      setStatus(propStatus);
      setLoading(false);
      return;
    }

    // Load from API if no prop provided
    const loadData = async () => {
      try {
        const data = await fetchBrowserVerificationStatus();
        setStatus(data);
      } catch (err) {
        console.debug('Failed to load browser verification status:', err);
        setStatus({
          ok: false,
          status: 'missing',
          verified_pages: null,
          error: 'Failed to load',
        });
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [propStatus]);

  if (loading || !status) {
    return (
      <div
        className={`inline-flex items-center gap-2 bg-gray-100 border border-gray-300 rounded-md px-3 py-2 text-sm text-gray-600 ${className}`}
      >
        <span>Browser check: loading…</span>
      </div>
    );
  }

  if (!status.ok || status.status === 'missing') {
    return (
      <div
        className={`inline-flex items-center gap-2 bg-gray-100 border border-gray-300 rounded-md px-3 py-2 text-sm text-gray-600 ${className}`}
      >
        <span>Browser: not verified</span>
      </div>
    );
  }

  if (status.status === 'partial') {
    const pageCount = status.verified_pages ? ` (${status.verified_pages} pages)` : '';
    return (
      <a
        href="/docs/atlas/index.html"
        target="_blank"
        rel="noopener noreferrer"
        className={`inline-flex items-center gap-2 bg-yellow-100 border border-yellow-300 rounded-md px-3 py-2 text-sm text-yellow-800 hover:bg-yellow-200 ${className}`}
      >
        <span>Browser: partial{pageCount}</span>
      </a>
    );
  }

  // status.status === 'verified'
  return (
    <a
      href="/docs/atlas/index.html"
      target="_blank"
      rel="noopener noreferrer"
      className={`inline-flex items-center gap-2 bg-green-100 border border-green-300 rounded-md px-3 py-2 text-sm text-green-800 hover:bg-green-200 ${className}`}
    >
      <span className="text-base">✓</span>
      <span className="font-medium">Browser: verified</span>
    </a>
  );
};

export default BrowserVerifiedBadge;

