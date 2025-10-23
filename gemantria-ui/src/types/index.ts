// Core processing result (matches actual system output)
export interface ProcessedNoun {
  surface: string;
  normalized: string;
  gematria: number;
  db: {
    present_in_bible_db: boolean;
    strong_number?: string;
    lemma_frequency?: number;
    verse_context: Array<{
      book: string;
      chapter: number;
      verse: number;
      text: string;
    }>;
  };
  llm: {
    provider: string;
    endpoint: string;
    confidence?: number;
  };
}

// Batch processing result (matches BatchResult)
export interface BatchProcessingResult {
  batch_id: string;
  config: {
    batch_size: number;
    allow_partial: boolean;
    partial_reason?: string;
  };
  nouns_processed: number;
  results: ProcessedNoun[];
  manifest: {
    input_count: number;
    processed_count: number;
    input_hashes: string[];
    result_hashes: string[];
    validation: string;
  };
  created_at: string;
}

// Pipeline state (matches PipelineState)
export interface PipelineState {
  book_name: string;
  mode: string;
  nouns: string[];
  batch_result?: BatchProcessingResult;
  conflicts: any[];
  predictions: any;
  metadata: any;
}

// UI-specific types
export interface HebrewInputProps {
  onProcess: (text: string) => Promise<ProcessedNoun>;
  placeholder?: string;
  showCalculation?: boolean;
}

export interface BatchProcessorProps {
  onBatchComplete: (result: BatchProcessingResult) => void;
  maxBatchSize?: number;
  allowPartial?: boolean;
}

export interface ResultsDashboardProps {
  results: ProcessedNoun[];
  batchInfo?: BatchProcessingResult;
  onNounSelect: (noun: ProcessedNoun) => void;
}

export interface NetworkAnalysisProps {
  nouns: ProcessedNoun[];
  relationships: 'shared_prime' | 'identical_value' | 'gcd_gt_1';
  maxConnections?: number;
}
