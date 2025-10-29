# ADR-001: Two-DB Safety (bible_db RO; gematria RW)
- Implemented explicit RO adapter for bible_db that denies writes pre-connection.
- Enforced `%s` parameterization and banned f-strings in DB `.execute(...)`.
- Validation node now augments code gematria with bible_db presence, Strong's number, lemma frequency, and limited verse context.
