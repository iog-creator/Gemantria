'use client';

import { useState, useRef, useEffect } from 'react';
import { validateHebrewInput, calculateGematria, generateCalculationString } from '@/lib/utils';
import { HebrewInputProps } from '@/types';
import { Calculator, AlertCircle, CheckCircle } from 'lucide-react';

export default function HebrewInput({ 
  onProcess, 
  placeholder = "הקלד טקסט עברי...", 
  showCalculation = true 
}: HebrewInputProps) {
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Real-time validation and calculation
  useEffect(() => {
    if (input.trim()) {
      const validation = validateHebrewInput(input);
      if (validation.isValid) {
        setError(null);
        const gematria = calculateGematria(validation.normalized);
        setResult({
          normalized: validation.normalized,
          gematria,
          calculation: generateCalculationString(validation.normalized)
        });
      } else {
        setError(validation.errors[0]);
        setResult(null);
      }
    } else {
      setError(null);
      setResult(null);
    }
  }, [input]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || error) return;

    setIsProcessing(true);
    try {
      const processed = await onProcess(input);
      setResult(processed);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Processing failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSubmit(e);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className={`
              w-full h-32 px-4 py-3 border-2 rounded-lg font-hebrew text-right text-lg
              focus:outline-none focus:ring-2 focus:ring-gold transition-colors
              ${error ? 'border-crimson' : 'border-gray-300 focus:border-gold'}
              ${isProcessing ? 'opacity-50' : ''}
            `}
            style={{ direction: 'rtl' }}
            disabled={isProcessing}
          />
          
          {/* Status indicator */}
          <div className="absolute top-3 left-3">
            {isProcessing ? (
              <div className="animate-spin w-5 h-5 border-2 border-gold border-t-transparent rounded-full" />
            ) : error ? (
              <AlertCircle className="w-5 h-5 text-crimson" />
            ) : result ? (
              <CheckCircle className="w-5 h-5 text-olive" />
            ) : null}
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="text-crimson text-sm flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}

        {/* Real-time calculation display */}
        {result && showCalculation && (
          <div className="bg-gray-50 p-4 rounded-lg border">
            <div className="flex items-center gap-2 mb-2">
              <Calculator className="w-4 h-4 text-gold" />
              <span className="font-semibold text-text">Gematria Calculation</span>
            </div>
            <div className="font-mono text-sm text-muted">
              {result.calculation}
            </div>
            <div className="mt-2 text-right">
              <span className="text-2xl font-bold text-gold">
                {result.gematria.toLocaleString()}
              </span>
            </div>
          </div>
        )}

        {/* Submit button */}
        <button
          type="submit"
          disabled={!input.trim() || !!error || isProcessing}
          className={`
            w-full py-3 px-6 rounded-lg font-semibold transition-colors
            ${!input.trim() || !!error || isProcessing
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gold text-white hover:bg-yellow-600 active:bg-yellow-700'
            }
          `}
        >
          {isProcessing ? 'Processing...' : 'Calculate Gematria'}
        </button>
      </form>

      {/* Keyboard shortcut hint */}
      <div className="mt-2 text-xs text-muted text-center">
        Press Cmd+Enter (Mac) or Ctrl+Enter (Windows) to submit
      </div>
    </div>
  );
}
