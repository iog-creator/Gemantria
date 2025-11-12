// PLAN-081: Browser-Verified Badge — links to browser verification screenshots
import React from 'react';

interface BrowserVerifiedBadgeProps {
  className?: string;
  releaseVersion?: string;
}

const BrowserVerifiedBadge: React.FC<BrowserVerifiedBadgeProps> = ({
  className = '',
  releaseVersion = 'v0.0.3',
}) => {
  const screenshotPaths = {
    index: `/share/releases/${releaseVersion}/webproof/browser_verified_index.png`,
    catalog: `/share/releases/${releaseVersion}/webproof/browser_verified_mcp_catalog_view.png`,
  };

  return (
    <div
      className={className}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '8px',
        backgroundColor: '#d4edda',
        border: '1px solid #c3e6cb',
        borderRadius: '6px',
        padding: '8px 12px',
        fontSize: '14px',
        color: '#155724',
      }}
    >
      <span style={{ fontSize: '16px' }}>✓</span>
      <span style={{ fontWeight: 500 }}>Browser-Verified</span>
      <span style={{ color: '#6c757d', fontSize: '12px' }}>|</span>
      <a
        href={screenshotPaths.index}
        target="_blank"
        rel="noopener noreferrer"
        style={{ color: '#155724', textDecoration: 'underline', cursor: 'pointer' }}
        title="View index page screenshot"
      >
        Index
      </a>
      <span style={{ color: '#6c757d' }}>•</span>
      <a
        href={screenshotPaths.catalog}
        target="_blank"
        rel="noopener noreferrer"
        style={{ color: '#155724', textDecoration: 'underline', cursor: 'pointer' }}
        title="View MCP catalog viewer screenshot"
      >
        Catalog
      </a>
    </div>
  );
};

export default BrowserVerifiedBadge;

