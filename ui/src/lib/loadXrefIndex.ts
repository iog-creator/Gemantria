// Load cross-reference index from derived artifacts

import { XrefIndex } from '../types/xrefs';

export async function loadXrefIndex(filePath: string = '/out/xrefs_index.v1.json'): Promise<XrefIndex> {
  try {
    const response = await fetch(filePath);
    if (!response.ok) {
      throw new Error(`Failed to load xref index: ${response.statusText}`);
    }
    const data = await response.json();
    
    // Validate schema
    if (data.schema !== 'ui-xrefs-index.v1') {
      console.warn(`Unexpected xref index schema: ${data.schema}`);
    }
    
    return data as XrefIndex;
  } catch (error) {
    console.error('Error loading xref index:', error);
    throw error;
  }
}

