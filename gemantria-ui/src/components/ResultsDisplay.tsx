'use client';

import { ProcessedNoun } from '@/types';
import { BookOpen, Hash, Database, Brain, ExternalLink } from 'lucide-react';

interface ResultsDisplayProps {
  results: ProcessedNoun[];
  onNounSelect?: (noun: ProcessedNoun) => void;
}

export default function ResultsDisplay({ results, onNounSelect }: ResultsDisplayProps) {
  if (results.length === 0) {
    return (
      <div className="text-center py-12 text-muted">
        <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-300" />
        <p>No results to display. Enter Hebrew text to see gematria calculations.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-text">Results ({results.length})</h2>
        <div className="text-sm text-muted">
          Gematria values calculated
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {results.map((noun, index) => (
          <div
            key={index}
            className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => onNounSelect?.(noun)}
          >
            {/* Hebrew text */}
            <div className="text-right mb-3">
              <div className="font-hebrew text-2xl text-text mb-1">
                {noun.surface}
              </div>
              {noun.normalized !== noun.surface && (
                <div className="font-hebrew text-lg text-muted">
                  {noun.normalized}
                </div>
              )}
            </div>

            {/* Gematria value */}
            <div className="text-center mb-3">
              <div className="text-3xl font-bold text-gold">
                {noun.gematria.toLocaleString()}
              </div>
            </div>

            {/* Database info */}
            {noun.db.present_in_bible_db && (
              <div className="flex items-center gap-2 text-sm text-olive mb-2">
                <Database className="w-4 h-4" />
                <span>Found in Bible database</span>
                {noun.db.strong_number && (
                  <span className="font-mono">({noun.db.strong_number})</span>
                )}
              </div>
            )}

            {/* Verse context */}
            {noun.db.verse_context.length > 0 && (
              <div className="text-xs text-muted mb-2">
                <div className="flex items-center gap-1 mb-1">
                  <BookOpen className="w-3 h-3" />
                  <span>Biblical references:</span>
                </div>
                <div className="space-y-1">
                  {noun.db.verse_context.slice(0, 2).map((verse, i) => (
                    <div key={i} className="font-mono">
                      {verse.book} {verse.chapter}:{verse.verse}
                    </div>
                  ))}
                  {noun.db.verse_context.length > 2 && (
                    <div className="text-gray-400">
                      +{noun.db.verse_context.length - 2} more
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* LLM info */}
            {noun.llm.confidence && (
              <div className="flex items-center gap-2 text-xs text-purple">
                <Brain className="w-3 h-3" />
                <span>AI Confidence: {Math.round(noun.llm.confidence * 100)}%</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
