WITH n AS (

  SELECT (j->>'lemma') AS lemma,

         (j->>'book') AS book,

         (j->>'hebrew') AS hebrew

  FROM jsonb_array_elements((pg_read_file('exports/unified_envelope_1000.json')::jsonb)->'nodes') j

)

SELECT 'empty_hebrew' AS issue, COUNT(*) AS n

FROM n WHERE COALESCE(hebrew,'')='';
