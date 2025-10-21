# ADR-001: Two-DB Safety (bible_db RO; gematria RW)
Decision: bible_db is read-only; parameterized SQL only. All writes go to gematria DB. RO enforcement and connection pooling added in PR-002.
