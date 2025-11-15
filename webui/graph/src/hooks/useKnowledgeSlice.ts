import { useState, useEffect } from "react";
import { KBWidgetProps, KBDocWidgetProps, normalizeKbDocs } from "../utils/kbAdapter";

/**
 * React hook for loading Knowledge Base documents.
 *
 * Fetches kb_docs.head.json from the public exports directory and normalizes it
 * using the KB adapter. Handles loading states and errors gracefully.
 *
 * @param kbUrl - URL path to kb_docs.head.json (default: "/exports/kb_docs.head.json")
 * @returns Object with docs, loading, error, and isEmpty flags
 */
export function useKnowledgeSlice(kbUrl: string = "/exports/kb_docs.head.json") {
  const [props, setProps] = useState<KBWidgetProps | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadKbDocs() {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(kbUrl);
        if (!response.ok) {
          // If file doesn't exist, use offline-safe default
          if (response.status === 404) {
            const offlineDefault = normalizeKbDocs(null);
            setProps(offlineDefault);
            setLoading(false);
            return;
          }
          throw new Error(`Failed to load KB docs: ${response.statusText}`);
        }

        const rawData = await response.json();
        const normalized = normalizeKbDocs(rawData);
        setProps(normalized);

        // Set error if db_off or not ok
        if (normalized.db_off || !normalized.ok) {
          setError(normalized.error || "KB docs unavailable");
        }
      } catch (err) {
        // On any error, use offline-safe default
        const offlineDefault = normalizeKbDocs(null);
        setProps(offlineDefault);
        setError(err instanceof Error ? err.message : "Unknown error occurred");
        console.error("Error loading KB docs:", err);
      } finally {
        setLoading(false);
      }
    }

    loadKbDocs();
  }, [kbUrl]);

  const docs: KBDocWidgetProps[] = props?.docs || [];
  const isEmpty = docs.length === 0;

  return {
    docs,
    loading,
    error,
    isEmpty,
    db_off: props?.db_off ?? true,
    ok: props?.ok ?? false,
  };
}

