
// webui/dashboard/src/utils/docsControlData.ts

// --- Interfaces based on DOC_CONTROL_PANEL_CONTRACT.md ---

export interface SummaryData {
    totals: {
        canonical: number;
        archive_candidates: number;
        unreviewed: number;
        total: number;
    };
    path_buckets: {
        ssot: number;
        archive: number;
        other: number;
    };
    generated_at: string; // RFC3339
}

export interface CanonicalDocument {
    path: string;
    title: string | null;
    doc_type: string | null;
    status: string;
    is_canonical: boolean;
    last_modified: string;
    size_bytes: number;
}

export interface CanonicalList {
    items: CanonicalDocument[];
    total: number;
    generated_at: string;
}

export interface ArchiveCandidateGroup {
    directory: string;
    count: number;
    example_paths: string[];
    confidence: "safe_cluster" | "mixed_cluster";
    notes: string;
}

export interface ArchiveCandidates {
    groups: ArchiveCandidateGroup[];
    total_groups: number;
    total_items: number;
    generated_at: string;
}

export interface UnreviewedDocument {
    path: string;
    doc_type: string | null;
    status: string;
    title: string | null;
    snippet: string;
    guess: string;
    last_modified: string;
}

export interface UnreviewedBatch {
    batch_id: string;
    items: UnreviewedDocument[];
    batch_size: number;
    remaining_estimate: number;
    generated_at: string;
}

export interface OrphanItem {
    path: string;
    type: "file" | "directory";
    size_bytes?: number;
    item_count?: number;
}

export interface OrphanCategory {
    name: string;
    description: string;
    items: OrphanItem[];
}

export interface Orphans {
    categories: OrphanCategory[];
    generated_at: string;
}

export interface ArchiveDryRunItem {
    from: string;
    to: string;
    reason: string;
    size_bytes: number;
}

export interface ArchiveDryRunGroup {
    directory: string;
    count: number;
    total_size_bytes: number;
}

export interface ArchiveDryRun {
    total_candidates: number;
    items: ArchiveDryRunItem[];
    groups: ArchiveDryRunGroup[];
    generated_at: string;
}

// --- Data Access Functions ---

const BASE_URL = '/exports/docs-control';

async function fetchJson<T>(filename: string): Promise<T> {
    const response = await fetch(`${BASE_URL}/${filename}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch ${filename}: ${response.statusText}`);
    }
    return response.json();
}

export const getDocsSummary = () => fetchJson<SummaryData>('summary.json');
export const getCanonicalDocs = () => fetchJson<CanonicalList>('canonical.json');
export const getArchiveCandidateGroups = () => fetchJson<ArchiveCandidates>('archive-candidates.json');
export const getUnreviewedBatch = () => fetchJson<UnreviewedBatch>('unreviewed-batch.json');
export const getOrphans = () => fetchJson<Orphans>('orphans.json');
export const getArchiveDryrun = () => fetchJson<ArchiveDryRun>('archive-dryrun.json');
