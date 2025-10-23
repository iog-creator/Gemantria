'use client';

import { useState } from 'react';
import HebrewInput from '@/components/HebrewInput';
import ResultsDisplay from '@/components/ResultsDisplay';
import { ProcessedNoun } from '@/types';
import { BookOpen, Calculator, Database } from 'lucide-react';

export default function Home() {
  const [results, setResults] = useState<ProcessedNoun[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  // Process Hebrew text using the API
  const processHebrewText = async (text: string): Promise<ProcessedNoun> => {
    const response = await fetch('/api/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error('Failed to process Hebrew text');
    }

    return response.json();
  };

  const handleProcess = async (text: string) => {
    setIsProcessing(true);
    try {
      const result = await processHebrewText(text);
      setResults(prev => [result, ...prev]);
    } catch (error) {
      console.error('Processing error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleNounSelect = (noun: ProcessedNoun) => {
    console.log('Selected noun:', noun);
    // In a real implementation, this would open a detailed view
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gold rounded-lg flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-text">Gemantria</h1>
            </div>
            <div className="text-sm text-muted">
              Hebrew Gematria Analysis
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Hero section */}
          <div className="text-center">
            <h2 className="text-4xl font-bold text-text mb-4">
              Hebrew Gematria Calculator
            </h2>
            <p className="text-xl text-muted max-w-2xl mx-auto">
              Enter Hebrew text to calculate gematria values, explore biblical references, 
              and discover numerical patterns in sacred texts.
            </p>
          </div>

          {/* Input section */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <HebrewInput 
              onProcess={handleProcess}
              placeholder="הקלד טקסט עברי כאן..."
              showCalculation={true}
            />
          </div>

          {/* Results section */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <ResultsDisplay 
              results={results}
              onNounSelect={handleNounSelect}
            />
          </div>

          {/* Features section */}
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
              <Calculator className="w-12 h-12 text-gold mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-text mb-2">Real-time Calculation</h3>
              <p className="text-muted">
                Instant gematria calculations with step-by-step breakdowns
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
              <Database className="w-12 h-12 text-olive mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-text mb-2">Biblical Integration</h3>
              <p className="text-muted">
                Connect with Strong's numbers and biblical references
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
              <BookOpen className="w-12 h-12 text-purple mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-text mb-2">Academic Accuracy</h3>
              <p className="text-muted">
                Mispar Hechrachi method with proper Hebrew normalization
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-muted">
            <p>Built with Next.js, TypeScript, and the Gemantria v2.0 pipeline</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
