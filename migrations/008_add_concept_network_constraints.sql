BEGIN;

-- Add unique constraint on concept_id for upsert operations
ALTER TABLE concept_network
ADD CONSTRAINT concept_network_concept_id_unique UNIQUE (concept_id);

-- Add unique constraint on concept_relations for upsert operations
ALTER TABLE concept_relations
ADD CONSTRAINT concept_relations_unique_pair UNIQUE (source_id, target_id);

COMMIT;
