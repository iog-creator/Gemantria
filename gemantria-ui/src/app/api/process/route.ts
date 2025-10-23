import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const { text } = await request.json();
    
    if (!text || typeof text !== 'string') {
      return NextResponse.json(
        { error: 'Text input is required' },
        { status: 400 }
      );
    }

    // For demo purposes, we'll use a simplified processing
    // In production, this would call the actual Python pipeline
    const result = await processHebrewText(text);
    
    return NextResponse.json(result);
  } catch (error) {
    console.error('Processing error:', error);
    return NextResponse.json(
      { error: 'Failed to process Hebrew text' },
      { status: 500 }
    );
  }
}

// Simplified processing function for demo
async function processHebrewText(text: string) {
  // Basic Hebrew normalization
  const normalized = text.replace(/[\u0591-\u05C7]/g, ''); // Remove nikud
  
  // Gematria calculation
  const gematria = calculateGematria(normalized);
  
  // Mock database lookup
  const dbInfo = {
    present_in_bible_db: Math.random() > 0.5,
    strong_number: Math.random() > 0.7 ? `H${Math.floor(Math.random() * 9000) + 1000}` : undefined,
    lemma_frequency: Math.random() > 0.6 ? Math.floor(Math.random() * 100) + 1 : undefined,
    verse_context: Math.random() > 0.8 ? [
      {
        book: 'Genesis',
        chapter: Math.floor(Math.random() * 50) + 1,
        verse: Math.floor(Math.random() * 20) + 1,
        text: 'Sample verse text in Hebrew...'
      }
    ] : []
  };
  
  return {
    surface: text,
    normalized,
    gematria,
    db: dbInfo,
    llm: {
      provider: 'lm_studio',
      endpoint: 'http://127.0.0.1:1234',
      confidence: Math.random() > 0.5 ? Math.random() : undefined
    }
  };
}

// Gematria calculation function
function calculateGematria(hebrewText: string): number {
  const map: { [key: string]: number } = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9, "י": 10,
    "כ": 20, "ך": 20, "ל": 30, "מ": 40, "ם": 40, "נ": 50, "ן": 50, "ס": 60, "ע": 70,
    "פ": 80, "ף": 80, "צ": 90, "ץ": 90, "ק": 100, "ר": 200, "ש": 300, "ת": 400
  };
  
  return hebrewText.split('').reduce((sum, char) => sum + (map[char] || 0), 0);
}
