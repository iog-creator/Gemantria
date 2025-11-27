// Temporary re-export to fix Vite module resolution cache issue
// This file re-exports everything from tileRegistry.tsx
// This file can be removed after Vite dev server restart

// Use a different import path to avoid circular reference
// Import from the .tsx file using a path that Vite will resolve
import type { TileConfig, TileSummaryProps, TileExpandedProps } from './tileRegistry.tsx';
import { getTilesByPosition, getTileById, tileRegistry } from './tileRegistry.tsx';

export type { TileConfig, TileSummaryProps, TileExpandedProps };
export { getTilesByPosition, getTileById, tileRegistry };
