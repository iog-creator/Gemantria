export type XRef = { book: string; chapter: number; verse: number; ref: string };
export type VerseSource = 'local' | 'api';

const SOURCE: VerseSource = (import.meta.env.VITE_VERSE_SOURCE as VerseSource) || 'local';
const API_URL = import.meta.env.VITE_VERSE_API_URL || '';

// Lazy-loaded local cache (built file takes precedence, else sample)
let localCache: Record<string, string> | null = null;
async function loadLocal(): Promise<Record<string, string>> {
  if (localCache) return localCache;
  try {
    // prefer generated file if present (vite will copy from ui/out)
    const gen = await fetch('/xrefs/verses.local.json');
    if (gen.ok) {
      localCache = await gen.json();
      return localCache!;
    }
  } catch {}
  // fallback sample bundled with the app
  const mod = await import('../data/verses.sample.json');
  localCache = mod.default as Record<string, string>;
  return localCache!;
}

export async function getVerseText(xr: XRef): Promise<string> {
  const key = `${xr.book}:${xr.chapter}:${xr.verse}`;
  if (SOURCE === 'api' && API_URL) {
    try {
      const url = `${API_URL}?book=${encodeURIComponent(xr.book)}&chapter=${xr.chapter}&verse=${xr.verse}`;
      const res = await fetch(url, { headers: { Accept: 'application/json' } });
      if (res.ok) {
        const data = await res.json();
        return (data?.text as string) || '';
      }
    } catch {/* fall through to local */}
  }
  const cache = await loadLocal();
  return cache[key] || '';
}

