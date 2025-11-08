// Cross-reference side panel - verse detail viewer

import React, { useEffect, useRef, useState } from 'react';
import { XrefReference, XrefNode } from '../types/xrefs';
import { getVerseText } from '../lib/verseProvider';

interface XrefSidePanelProps {
  selectedXref: XrefReference | null;
  node: XrefNode | null;
  onClose: () => void;
}

const XrefSidePanel: React.FC<XrefSidePanelProps> = ({
  selectedXref,
  node,
  onClose,
}) => {
  const [verseText, setVerseText] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const panelRef = useRef<HTMLDivElement | null>(null);
  const closeRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (selectedXref) {
      setLoading(true);
      setError('');
      getVerseText(selectedXref)
        .then((txt) => setVerseText(txt || '(no text available)'))
        .catch(() => setError('Failed to load verse text'))
        .finally(() => setLoading(false));
    }
  }, [selectedXref]);

  // Scroll-lock + focus management + keyboard handlers
  useEffect(() => {
    if (!selectedXref) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.stopPropagation();
        onClose();
      }
      if (e.key === 'Tab' && panelRef.current) {
        // Simple focus trap
        const focusables = panelRef.current.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusables.length === 0) return;
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        const active = document.activeElement as HTMLElement | null;
        if (e.shiftKey && active === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && active === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    document.addEventListener('keydown', onKey, true);
    // autofocus close button
    setTimeout(() => closeRef.current?.focus(), 0);
    return () => {
      document.body.style.overflow = prevOverflow;
      document.removeEventListener('keydown', onKey, true);
    };
  }, [selectedXref, onClose]);

  if (!selectedXref || !node) {
    return null;
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Cross reference ${selectedXref?.ref ?? ''}`}
      ref={panelRef}
      style={{
        position: 'fixed',
        top: 0,
        right: 0,
        width: '400px',
        height: '100vh',
        backgroundColor: '#ffffff',
        boxShadow: '-2px 0 8px rgba(0,0,0,0.1)',
        padding: '1.5rem',
        overflowY: 'auto',
        zIndex: 1000,
      }}
    >
      {/* Close button */}
      <button
        ref={closeRef}
        onClick={onClose}
        aria-label="Close"
        style={{
          position: 'absolute',
          top: '1rem',
          right: '1rem',
          background: 'transparent',
          border: 'none',
          fontSize: '1.5rem',
          cursor: 'pointer',
          color: '#666',
          padding: '0.25rem 0.5rem',
          outline: 'none',
        }}
        onFocus={(e) => {
          e.currentTarget.style.outline = '2px solid #01579b';
          e.currentTarget.style.outlineOffset = '2px';
        }}
        onBlur={(e) => {
          e.currentTarget.style.outline = 'none';
        }}
        title="Close"
      >
        ×
      </button>

      {/* Header */}
      <h2 style={{ marginTop: 0, marginBottom: '1rem', color: '#01579b' }}>
        Cross-Reference Detail
      </h2>

      {/* Selected reference */}
      <div
        style={{
          padding: '1rem',
          backgroundColor: '#e1f5fe',
          borderRadius: '8px',
          marginBottom: '1.5rem',
        }}
      >
        <div style={{ fontWeight: '600', fontSize: '1.1rem', marginBottom: '0.5rem' }}>
          {selectedXref.ref}
        </div>
        <div style={{ fontSize: '0.85rem', color: '#666', marginBottom: '0.5rem' }}>
          {selectedXref.book} {selectedXref.chapter}:{selectedXref.verse}
        </div>
        {loading && <div style={{ fontSize: '0.9rem', color: '#666', fontStyle: 'italic' }}>Loading verse…</div>}
        {error && <div style={{ fontSize: '0.9rem', color: '#d32f2f' }}>{error}</div>}
        {!loading && !error && verseText && (
          <div style={{ fontSize: '0.9rem', color: '#333', marginTop: '0.5rem', whiteSpace: 'pre-wrap' }}>
            {verseText}
          </div>
        )}
      </div>

      {/* Source noun details */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem', color: '#333' }}>
          Source Noun
        </h3>
        <div style={{ padding: '1rem', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem', fontWeight: '600' }}>
            {node.he}
          </div>
          <div style={{ fontSize: '0.85rem', color: '#666' }}>
            Gematria: <span style={{ fontWeight: '600' }}>{node.gm}</span>
          </div>
          <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.25rem' }}>
            Total References: <span style={{ fontWeight: '600' }}>{node.xref_count}</span>
          </div>
        </div>
      </div>

      {/* All references for this noun */}
      <div>
        <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem', color: '#333' }}>
          All Cross-References ({node.xref_count})
        </h3>
        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
          {node.xrefs.map((xref, index) => (
            <div
              key={`${xref.book}-${xref.chapter}-${xref.verse}-${index}`}
              style={{
                padding: '0.75rem',
                backgroundColor:
                  xref.ref === selectedXref.ref ? '#e1f5fe' : '#fafafa',
                borderLeft:
                  xref.ref === selectedXref.ref ? '3px solid #01579b' : '3px solid transparent',
                marginBottom: '0.5rem',
                borderRadius: '4px',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>
                {xref.ref}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.25rem' }}>
                {xref.book} {xref.chapter}:{xref.verse}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default XrefSidePanel;

