/**
 * Knowledge Base adapter for downstream apps (StoryMaker, BibleScholar).
 *
 * Transforms the canonical `kb_docs.head.json` export into a simple, typed interface.
 * Hermetic (file-only, no DB calls) and fail-closed (offline-safe defaults when file is missing or invalid).
 *
 * See `docs/SSOT/KB_WIDGETS.md` for the KB export schema.
 */

export interface KBDocWidgetProps {
  id: string;
  title: string;
  section: string;
  slug: string;
  tags: string[];
  preview: string;
  created_at: string;
}

export interface KBWidgetProps {
  docs: KBDocWidgetProps[];
  db_off: boolean;
  ok: boolean;
  error: string | null;
  generated_at: string | null;
  source: {
    path: string;
  };
}

const OFFLINE_SAFE_DEFAULT: KBWidgetProps = {
  docs: [],
  db_off: true,
  ok: false,
  error: "KB docs unavailable (offline or file missing)",
  generated_at: null,
  source: {
    path: "share/atlas/control_plane/kb_docs.head.json",
  },
};

/**
 * Normalize KB docs JSON to typed widget props.
 *
 * Handles:
 * - db_off / ok:false / empty docs -> returns empty array
 * - malformed entries -> ignores bad docs, doesn't crash
 * - missing required fields -> uses safe defaults
 *
 * @param json - Raw JSON from kb_docs.head.json
 * @returns Normalized KB widget props
 */
export function normalizeKbDocs(json: unknown): KBWidgetProps {
  if (!json || typeof json !== "object") {
    return OFFLINE_SAFE_DEFAULT;
  }

  const obj = json as Record<string, unknown>;

  // Check for db_off or ok:false
  const db_off = obj.db_off === true;
  const ok = obj.ok === true;
  const error = typeof obj.error === "string" ? obj.error : null;
  const generated_at = typeof obj.generated_at === "string" ? obj.generated_at : null;

  // If db_off or not ok, return offline-safe default
  if (db_off || !ok) {
    return {
      ...OFFLINE_SAFE_DEFAULT,
      db_off,
      ok,
      error: error || OFFLINE_SAFE_DEFAULT.error,
      generated_at,
    };
  }

  // Parse docs array
  const docs: KBDocWidgetProps[] = [];
  if (Array.isArray(obj.docs)) {
    for (const doc of obj.docs) {
      if (!doc || typeof doc !== "object") {
        continue; // Skip malformed entries
      }

      const docObj = doc as Record<string, unknown>;

      // Validate required fields
      if (
        typeof docObj.id === "string" &&
        typeof docObj.title === "string" &&
        typeof docObj.slug === "string"
      ) {
        docs.push({
          id: docObj.id,
          title: docObj.title,
          section: typeof docObj.section === "string" ? docObj.section : "",
          slug: docObj.slug,
          tags: Array.isArray(docObj.tags) ? (docObj.tags as string[]) : [],
          preview: typeof docObj.preview === "string" ? docObj.preview : "",
          created_at: typeof docObj.created_at === "string" ? docObj.created_at : "",
        });
      }
      // Silently skip invalid docs (fail-safe)
    }
  }

    const sourceObj = obj.source && typeof obj.source === "object" ? (obj.source as Record<string, unknown>) : null;
    const sourcePath = sourceObj && typeof sourceObj.path === "string" ? sourceObj.path : OFFLINE_SAFE_DEFAULT.source.path;

    return {
      docs,
      db_off: false,
      ok: true,
      error: null,
      generated_at,
      source: {
        path: sourcePath,
      },
    };
}

