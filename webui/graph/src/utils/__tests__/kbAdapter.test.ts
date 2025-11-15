import { normalizeKbDocs } from "../kbAdapter";

describe("normalizeKbDocs", () => {
  test("valid kb_docs JSON -> list of docs", () => {
    const validJson = {
      schema: "knowledge",
      generated_at: "2025-11-15T12:00:00Z",
      ok: true,
      connection_ok: true,
      docs: [
        {
          id: "doc-1",
          title: "Test Document 1",
          section: "general",
          slug: "test-document-1",
          tags: ["test", "example"],
          preview: "This is a test document preview...",
          created_at: "2025-11-15T10:00:00Z",
        },
        {
          id: "doc-2",
          title: "Another Valid Doc",
          section: "bible",
          slug: "another-valid-doc",
          tags: ["bible"],
          preview: "Another preview text",
          created_at: "2025-11-15T11:00:00Z",
        },
      ],
      source: {
        path: "share/atlas/control_plane/kb_docs.head.json",
      },
    };

    const result = normalizeKbDocs(validJson);

    expect(result.ok).toBe(true);
    expect(result.db_off).toBe(false);
    expect(result.docs).toHaveLength(2);
    expect(result.docs[0].title).toBe("Test Document 1");
    expect(result.docs[0].section).toBe("general");
    expect(result.docs[1].title).toBe("Another Valid Doc");
  });

  test("db_off / ok:false / docs: [] -> empty array", () => {
    const dbOffJson = {
      ok: false,
      db_off: true,
      error: "Database unavailable",
      docs: [],
      generated_at: null,
    };

    const result = normalizeKbDocs(dbOffJson);

    expect(result.ok).toBe(false);
    expect(result.db_off).toBe(true);
    expect(result.docs).toHaveLength(0);
    expect(result.error).toBe("Database unavailable");
  });

  test("malformed docs -> ignored, no throw", () => {
    const malformedJson = {
      ok: true,
      db_off: false,
      docs: [
        {
          id: "valid-doc",
          title: "Valid Document",
          slug: "valid-doc",
        },
        null, // Invalid entry
        {
          // Missing required fields
          title: "Invalid Doc",
        },
        {
          id: 123, // Wrong type
          title: "Another Invalid",
          slug: "another-invalid",
        },
      ],
    };

    const result = normalizeKbDocs(malformedJson);

    expect(result.ok).toBe(true);
    expect(result.docs).toHaveLength(1); // Only valid doc included
    expect(result.docs[0].title).toBe("Valid Document");
  });

  test("null/undefined/invalid input -> offline-safe default", () => {
    expect(normalizeKbDocs(null)).toEqual(
      expect.objectContaining({
        db_off: true,
        ok: false,
        docs: [],
      })
    );

    expect(normalizeKbDocs(undefined)).toEqual(
      expect.objectContaining({
        db_off: true,
        ok: false,
        docs: [],
      })
    );

    expect(normalizeKbDocs("not an object")).toEqual(
      expect.objectContaining({
        db_off: true,
        ok: false,
        docs: [],
      })
    );
  });

  test("empty docs array -> returns empty array", () => {
    const emptyJson = {
      ok: true,
      db_off: false,
      docs: [],
      generated_at: "2025-11-15T12:00:00Z",
    };

    const result = normalizeKbDocs(emptyJson);

    expect(result.ok).toBe(true);
    expect(result.db_off).toBe(false);
    expect(result.docs).toHaveLength(0);
  });

  test("missing optional fields -> uses safe defaults", () => {
    const minimalJson = {
      ok: true,
      db_off: false,
      docs: [
        {
          id: "minimal-doc",
          title: "Minimal Document",
          slug: "minimal-doc",
          // Missing: section, tags, preview, created_at
        },
      ],
    };

    const result = normalizeKbDocs(minimalJson);

    expect(result.docs).toHaveLength(1);
    expect(result.docs[0].section).toBe("");
    expect(result.docs[0].tags).toEqual([]);
    expect(result.docs[0].preview).toBe("");
    expect(result.docs[0].created_at).toBe("");
  });
});

