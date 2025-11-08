// Cross-reference chips component - hoverable verse badges

import React, { useState } from 'react';
import { XrefReference } from '../types/xrefs';

interface XrefChipsProps {
  xrefs: XrefReference[];
  onChipClick?: (xref: XrefReference) => void;
  maxVisible?: number;
}

const XrefChips: React.FC<XrefChipsProps> = ({
  xrefs,
  onChipClick,
  maxVisible = 5,
}) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  if (!xrefs || xrefs.length === 0) {
    return (
      <div style={{ fontSize: '0.85rem', color: '#999', fontStyle: 'italic' }}>
        No cross-references
      </div>
    );
  }

  const visibleXrefs = xrefs.slice(0, maxVisible);
  const remainingCount = xrefs.length - maxVisible;

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
      {visibleXrefs.map((xref, index) => (
        <button
          key={`${xref.book}-${xref.chapter}-${xref.verse}-${index}`}
          onClick={() => onChipClick?.(xref)}
          onMouseEnter={() => setHoveredIndex(index)}
          onMouseLeave={() => setHoveredIndex(null)}
          style={{
            padding: '0.25rem 0.5rem',
            fontSize: '0.75rem',
            backgroundColor: hoveredIndex === index ? '#01579b' : '#e1f5fe',
            color: hoveredIndex === index ? '#ffffff' : '#01579b',
            border: '1px solid #01579b',
            borderRadius: '12px',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            fontWeight: hoveredIndex === index ? '600' : '400',
            whiteSpace: 'nowrap',
          }}
          title={`${xref.book} ${xref.chapter}:${xref.verse}`}
        >
          {xref.book.slice(0, 3)} {xref.chapter}:{xref.verse}
        </button>
      ))}
      {remainingCount > 0 && (
        <div
          style={{
            padding: '0.25rem 0.5rem',
            fontSize: '0.75rem',
            backgroundColor: '#f5f5f5',
            color: '#666',
            border: '1px solid #ddd',
            borderRadius: '12px',
            whiteSpace: 'nowrap',
          }}
        >
          +{remainingCount} more
        </div>
      )}
    </div>
  );
};

export default XrefChips;

