/**
 * Data loader utilities for Orchestrator Console v2.
 *
 * Phase 20.4 will implement actual fetch logic for:
 * - SSOT surface
 * - Control-plane exports
 * - Docs-control exports
 * - Orchestrator/OA surfaces
 * - Phase summaries
 *
 * For now, these are stubs that return undefined or empty structures.
 */

export async function loadJson<T = unknown>(path: string): Promise<T | undefined> {
    try {
        const res = await fetch(path);
        if (!res.ok) return undefined;
        return await res.json();
    } catch (err) {
        console.warn("Failed to load:", path, err);
        return undefined;
    }
}

export async function loadText(path: string): Promise<string | undefined> {
    try {
        const res = await fetch(path);
        if (!res.ok) return undefined;
        return await res.text();
    } catch (err) {
        console.warn("Failed to load:", path, err);
        return undefined;
    }
}
