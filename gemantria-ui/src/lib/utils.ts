import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Hebrew text validation
export function validateHebrewInput(text: string): {
  isValid: boolean;
  normalized: string;
  errors: string[];
} {
  const errors: string[] = [];
  
  // Check for Hebrew characters
  if (!/[\u0590-\u05FF]/.test(text)) {
    errors.push('Input must contain Hebrew characters');
  }
  
  // Check length
  if (text.length > 1000) {
    errors.push('Input too long (max 1000 characters)');
  }
  
  // Basic normalization (simplified version)
  const normalized = text.replace(/[\u0591-\u05C7]/g, ''); // Remove nikud
  
  return {
    isValid: errors.length === 0,
    normalized,
    errors
  };
}

// Gematria calculation (simplified version for demo)
export function calculateGematria(hebrewText: string): number {
  const map: { [key: string]: number } = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9, "י": 10,
    "כ": 20, "ך": 20, "ל": 30, "מ": 40, "ם": 40, "נ": 50, "ן": 50, "ס": 60, "ע": 70,
    "פ": 80, "ף": 80, "צ": 90, "ץ": 90, "ק": 100, "ר": 200, "ש": 300, "ת": 400
  };
  
  return hebrewText.split('').reduce((sum, char) => sum + (map[char] || 0), 0);
}

// Generate calculation string
export function generateCalculationString(hebrewText: string): string {
  const map: { [key: string]: number } = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9, "י": 10,
    "כ": 20, "ך": 20, "ל": 30, "מ": 40, "ם": 40, "נ": 50, "ן": 50, "ס": 60, "ע": 70,
    "פ": 80, "ף": 80, "צ": 90, "ץ": 90, "ק": 100, "ר": 200, "ש": 300, "ת": 400
  };
  
  const parts = hebrewText.split('').map(char => `${char}(${map[char] || 0})`);
  const total = calculateGematria(hebrewText);
  return parts.join(' + ') + ` = ${total}`;
}

// Format gematria value with proper Hebrew display
export function formatGematriaValue(value: number): string {
  return value.toLocaleString();
}
