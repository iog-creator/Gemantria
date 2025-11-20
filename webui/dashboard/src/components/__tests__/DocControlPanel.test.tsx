/**
 * NOTE: Webui tests are not yet wired into any test runner.
 * This file is a placeholder for future vitest/jest integration.
 * Currently, `npm run build` is the primary safety check for this package.
 * 
 * To run these tests in the future:
 * 1. Install test framework (vitest or jest) and @testing-library/react
 * 2. Add "test" script to package.json
 * 3. Configure test runner to find *.test.tsx files
 */

import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import DocControlPanel from "../DocControlPanel";
import * as dataUtils from "../../utils/docsControlData";

// Mock the data utils
jest.mock("../../utils/docsControlData");

const mockSummary = {
    totals: {
        canonical: 10,
        archive_candidates: 5,
        unreviewed: 20,
        total: 100,
    },
    path_buckets: {
        ssot: 5,
        archive: 10,
        other: 85,
    },
    generated_at: "2025-11-19T08:00:00Z",
};

const mockCanonical = {
    items: [
        {
            path: "docs/SSOT/test.md",
            title: "Test Doc",
            doc_type: "ssot",
            status: "canonical",
            is_canonical: true,
            last_modified: "2025-11-19T08:00:00Z",
            size_bytes: 100,
        },
    ],
    total: 1,
    generated_at: "2025-11-19T08:00:00Z",
};

const mockCandidates = {
    groups: [
        {
            directory: "archive/test/",
            count: 5,
            example_paths: ["archive/test/file1.txt"],
            confidence: "safe_cluster",
            notes: "Safe to delete",
        },
    ],
    total_groups: 1,
    total_items: 5,
    generated_at: "2025-11-19T08:00:00Z",
};

const mockUnreviewed = {
    batch_id: "batch-1",
    items: [
        {
            path: "docs/notes/random.md",
            doc_type: "note",
            status: "unreviewed",
            title: "Random Note",
            snippet: "Some content",
            guess: "note",
            last_modified: "2025-11-19T08:00:00Z",
        },
    ],
    batch_size: 20,
    remaining_estimate: 19,
    generated_at: "2025-11-19T08:00:00Z",
};

const mockOrphans = {
    categories: [],
    generated_at: "2025-11-19T08:00:00Z",
};

const mockDryrun = {
    total_candidates: 5,
    items: [],
    groups: [],
    generated_at: "2025-11-19T08:00:00Z",
};

describe("DocControlPanel", () => {
    beforeEach(() => {
        (dataUtils.getDocsSummary as jest.Mock).mockResolvedValue(mockSummary);
        (dataUtils.getCanonicalDocs as jest.Mock).mockResolvedValue(mockCanonical);
        (dataUtils.getArchiveCandidateGroups as jest.Mock).mockResolvedValue(mockCandidates);
        (dataUtils.getUnreviewedBatch as jest.Mock).mockResolvedValue(mockUnreviewed);
        (dataUtils.getOrphans as jest.Mock).mockResolvedValue(mockOrphans);
        (dataUtils.getArchiveDryrun as jest.Mock).mockResolvedValue(mockDryrun);
    });

    test("renders summary tiles and default overview tab", async () => {
        render(<DocControlPanel />);

        await waitFor(() => {
            expect(screen.getByText("Doc Control Panel")).toBeInTheDocument();
        });

        expect(screen.getByText("Total Docs")).toBeInTheDocument();
        expect(screen.getByText("100")).toBeInTheDocument();
        expect(screen.getByText("Canonical")).toBeInTheDocument();
        expect(screen.getByText("10")).toBeInTheDocument();
    });

    test("switches tabs and displays content", async () => {
        render(<DocControlPanel />);

        await waitFor(() => {
            expect(screen.getByText("Doc Control Panel")).toBeInTheDocument();
        });

        // Switch to Canonical tab
        fireEvent.click(screen.getByText("Canonical"));
        expect(screen.getByText("Canonical Documents")).toBeInTheDocument();
        expect(screen.getByText("docs/SSOT/test.md")).toBeInTheDocument();

        // Switch to Archive Candidates tab
        fireEvent.click(screen.getByText("Archive Candidates"));
        expect(screen.getByText("archive/test/")).toBeInTheDocument();

        // Switch to Unreviewed tab
        fireEvent.click(screen.getByText("Unreviewed"));
        expect(screen.getByText("docs/notes/random.md")).toBeInTheDocument();
    });
});
