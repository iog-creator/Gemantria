--
-- PostgreSQL database dump
--

\restrict VU1XxeL3sy2r61aywhnBdThL1lbZKgXccesTVwRY7evw6yg8vaDyoW9HaBbSEMP

-- Dumped from database version 17.6 (Ubuntu 17.6-0ubuntu0.25.04.1)
-- Dumped by pg_dump version 17.6 (Ubuntu 17.6-0ubuntu0.25.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: gematria; Type: SCHEMA; Schema: -; Owner: mccoy
--

CREATE SCHEMA gematria;


ALTER SCHEMA gematria OWNER TO mccoy;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: mccoy
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO mccoy;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: mccoy
--

COMMENT ON SCHEMA public IS '';


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


--
-- Name: refresh_metrics_materialized(); Type: FUNCTION; Schema: public; Owner: mccoy
--

CREATE FUNCTION public.refresh_metrics_materialized() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_node_latency_7d;
END $$;


ALTER FUNCTION public.refresh_metrics_materialized() OWNER TO mccoy;

--
-- Name: update_book_concept_count(); Type: FUNCTION; Schema: public; Owner: mccoy
--

CREATE FUNCTION public.update_book_concept_count() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE books 
    SET concept_count = (
        SELECT COUNT(*) FROM concepts WHERE book_id = NEW.book_id
    ),
    last_updated = CURRENT_TIMESTAMP
    WHERE id = NEW.book_id;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_book_concept_count() OWNER TO mccoy;

--
-- Name: update_concept_metadata_updated_at(); Type: FUNCTION; Schema: public; Owner: mccoy
--

CREATE FUNCTION public.update_concept_metadata_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_concept_metadata_updated_at() OWNER TO mccoy;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: mccoy
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO mccoy;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: concept_centrality; Type: TABLE; Schema: gematria; Owner: mccoy
--

CREATE TABLE gematria.concept_centrality (
    concept_id uuid NOT NULL,
    degree double precision,
    betweenness double precision,
    closeness double precision,
    eigenvector double precision,
    metrics_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE gematria.concept_centrality OWNER TO mccoy;

--
-- Name: concept_clusters; Type: TABLE; Schema: gematria; Owner: mccoy
--

CREATE TABLE gematria.concept_clusters (
    concept_id uuid NOT NULL,
    cluster_id integer,
    cluster_center boolean DEFAULT false,
    confidence numeric(4,3),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE gematria.concept_clusters OWNER TO mccoy;

--
-- Name: concept_network; Type: TABLE; Schema: gematria; Owner: mccoy
--

CREATE TABLE gematria.concept_network (
    id bigint NOT NULL,
    concept_id uuid NOT NULL,
    embedding public.vector(1024),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE gematria.concept_network OWNER TO mccoy;

--
-- Name: concept_network_id_seq; Type: SEQUENCE; Schema: gematria; Owner: mccoy
--

CREATE SEQUENCE gematria.concept_network_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE gematria.concept_network_id_seq OWNER TO mccoy;

--
-- Name: concept_network_id_seq; Type: SEQUENCE OWNED BY; Schema: gematria; Owner: mccoy
--

ALTER SEQUENCE gematria.concept_network_id_seq OWNED BY gematria.concept_network.id;


--
-- Name: concept_relations; Type: TABLE; Schema: gematria; Owner: mccoy
--

CREATE TABLE gematria.concept_relations (
    relation_id uuid DEFAULT gen_random_uuid() NOT NULL,
    src_concept_id uuid NOT NULL,
    dst_concept_id uuid NOT NULL,
    relation_type text NOT NULL,
    weight numeric(6,5) DEFAULT 0.00000 NOT NULL,
    evidence jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE gematria.concept_relations OWNER TO mccoy;

--
-- Name: concepts; Type: TABLE; Schema: gematria; Owner: mccoy
--

CREATE TABLE gematria.concepts (
    concept_id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    hebrew_text text,
    gematria_value integer,
    strong_number text,
    primary_verse text,
    book text,
    chapter integer,
    freq integer,
    content_hash text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE gematria.concepts OWNER TO mccoy;

--
-- Name: noun_occurrences; Type: TABLE; Schema: gematria; Owner: mccoy
--

CREATE TABLE gematria.noun_occurrences (
    noun_id bigint NOT NULL,
    verse_id bigint NOT NULL,
    token_idx integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE gematria.noun_occurrences OWNER TO mccoy;

--
-- Name: nouns; Type: TABLE; Schema: gematria; Owner: mccoy
--

CREATE TABLE gematria.nouns (
    id bigint NOT NULL,
    lemma text NOT NULL,
    language text DEFAULT 'he'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE gematria.nouns OWNER TO mccoy;

--
-- Name: nouns_id_seq; Type: SEQUENCE; Schema: gematria; Owner: mccoy
--

CREATE SEQUENCE gematria.nouns_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE gematria.nouns_id_seq OWNER TO mccoy;

--
-- Name: nouns_id_seq; Type: SEQUENCE OWNED BY; Schema: gematria; Owner: mccoy
--

ALTER SEQUENCE gematria.nouns_id_seq OWNED BY gematria.nouns.id;


--
-- Name: ai_enrichment_log; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.ai_enrichment_log (
    id bigint NOT NULL,
    run_id uuid NOT NULL,
    node text NOT NULL,
    noun_id uuid NOT NULL,
    model_name text NOT NULL,
    confidence_model text,
    confidence_score numeric(5,4),
    insights text NOT NULL,
    significance text NOT NULL,
    tokens_used integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    CONSTRAINT ai_enrichment_log_confidence_score_check CHECK (((confidence_score >= (0)::numeric) AND (confidence_score <= (1)::numeric)))
);


ALTER TABLE public.ai_enrichment_log OWNER TO mccoy;

--
-- Name: ai_enrichment_log_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.ai_enrichment_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ai_enrichment_log_id_seq OWNER TO mccoy;

--
-- Name: ai_enrichment_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.ai_enrichment_log_id_seq OWNED BY public.ai_enrichment_log.id;


--
-- Name: books; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.books (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    hebrew_name character varying(100),
    testament character varying(20) NOT NULL,
    category character varying(50) NOT NULL,
    book_number integer NOT NULL,
    concept_count integer DEFAULT 0,
    integration_status character varying(20) DEFAULT 'pending'::character varying,
    integration_date timestamp without time zone,
    last_updated timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    notes text,
    analysis_file character varying(255),
    CONSTRAINT books_integration_status_check CHECK (((integration_status)::text = ANY ((ARRAY['pending'::character varying, 'partial'::character varying, 'complete'::character varying, 'needs_review'::character varying])::text[]))),
    CONSTRAINT books_testament_check CHECK (((testament)::text = ANY ((ARRAY['OT'::character varying, 'NT'::character varying])::text[])))
);


ALTER TABLE public.books OWNER TO mccoy;

--
-- Name: TABLE books; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON TABLE public.books IS 'Master list of all biblical books with integration status';


--
-- Name: COLUMN books.integration_status; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.books.integration_status IS 'pending = not started, partial = some concepts added, complete = fully integrated';


--
-- Name: books_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.books_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.books_id_seq OWNER TO mccoy;

--
-- Name: books_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.books_id_seq OWNED BY public.books.id;


--
-- Name: books_summary; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.books_summary AS
SELECT
    NULL::integer AS id,
    NULL::character varying(100) AS name,
    NULL::character varying(100) AS hebrew_name,
    NULL::character varying(20) AS testament,
    NULL::character varying(50) AS category,
    NULL::integer AS book_number,
    NULL::integer AS concept_count,
    NULL::bigint AS actual_concept_count,
    NULL::character varying(20) AS integration_status,
    NULL::timestamp without time zone AS integration_date,
    NULL::character varying(255) AS analysis_file;


ALTER VIEW public.books_summary OWNER TO mccoy;

--
-- Name: checkpointer_state; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.checkpointer_state (
    workflow text NOT NULL,
    thread_id text NOT NULL,
    checkpoint_id text NOT NULL,
    parent_checkpoint_id text,
    checkpoint jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.checkpointer_state OWNER TO mccoy;

--
-- Name: checkpointer_writes; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.checkpointer_writes (
    workflow text NOT NULL,
    thread_id text NOT NULL,
    checkpoint_id text NOT NULL,
    task_id text NOT NULL,
    idx integer NOT NULL,
    channel text NOT NULL,
    value jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.checkpointer_writes OWNER TO mccoy;

--
-- Name: cluster_metrics; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.cluster_metrics (
    cluster_id integer NOT NULL,
    size integer NOT NULL,
    density double precision,
    modularity double precision,
    semantic_diversity double precision,
    top_examples uuid[],
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.cluster_metrics OWNER TO mccoy;

--
-- Name: concept_centrality; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.concept_centrality (
    concept_id uuid NOT NULL,
    degree double precision,
    betweenness double precision,
    eigenvector double precision,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.concept_centrality OWNER TO mccoy;

--
-- Name: concept_clusters; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.concept_clusters (
    concept_id uuid NOT NULL,
    cluster_id integer NOT NULL,
    modularity double precision,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.concept_clusters OWNER TO mccoy;

--
-- Name: concept_metadata; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.concept_metadata (
    concept_id uuid NOT NULL,
    label text NOT NULL,
    description text,
    source text,
    language text DEFAULT 'he'::text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.concept_metadata OWNER TO mccoy;

--
-- Name: concept_metrics; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.concept_metrics (
    concept_id uuid NOT NULL,
    cluster_id integer,
    semantic_cohesion double precision,
    bridge_score double precision,
    diversity_local double precision,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.concept_metrics OWNER TO mccoy;

--
-- Name: concept_network; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.concept_network (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    concept_id uuid NOT NULL,
    embedding public.vector(1024) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    embedding_bge_m3 public.vector(1024)
);


ALTER TABLE public.concept_network OWNER TO mccoy;

--
-- Name: concept_relations; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.concept_relations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    source_id uuid NOT NULL,
    target_id uuid NOT NULL,
    cosine double precision NOT NULL,
    rerank_score double precision,
    decided_yes boolean,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    edge_strength numeric(6,5),
    rerank_model text,
    rerank_at timestamp with time zone DEFAULT now(),
    similarity numeric(6,5),
    relation_type text
);


ALTER TABLE public.concept_relations OWNER TO mccoy;

--
-- Name: concept_rerank_cache; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.concept_rerank_cache (
    source_id bigint NOT NULL,
    target_id bigint NOT NULL,
    model text NOT NULL,
    score real NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.concept_rerank_cache OWNER TO mccoy;

--
-- Name: concepts; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.concepts (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    hebrew_text character varying(255) NOT NULL,
    hebrew_with_nikud character varying(255),
    gematria_value integer NOT NULL,
    gematria_calculation text,
    english_meaning text NOT NULL,
    book_id integer,
    book_source character varying(100),
    verse_references text[],
    primary_verse text,
    context_passage text,
    theological_category character varying(100),
    semantic_tags text[],
    insights text NOT NULL,
    theological_significance text NOT NULL,
    cross_references text[],
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(50) DEFAULT 'grok'::character varying,
    validation_status character varying(20) DEFAULT 'pending'::character varying,
    strong_number character varying(10),
    verse_occurrence_count integer DEFAULT 0,
    embedding public.vector(768),
    doctrinal_tags text[] DEFAULT '{}'::text[],
    temporal_eras text[] DEFAULT '{}'::text[],
    spatial_contexts text[] DEFAULT '{}'::text[],
    typological_links jsonb DEFAULT '[]'::jsonb,
    verse_occurrence_id character varying(100),
    verse_context text,
    usage_context text,
    CONSTRAINT concepts_validation_status_check CHECK (((validation_status)::text = ANY ((ARRAY['pending'::character varying, 'validated'::character varying, 'needs_correction'::character varying])::text[]))),
    CONSTRAINT non_empty_hebrew CHECK ((length(TRIM(BOTH FROM hebrew_text)) > 0)),
    CONSTRAINT non_empty_meaning CHECK ((length(TRIM(BOTH FROM english_meaning)) > 0)),
    CONSTRAINT valid_gematria CHECK ((gematria_value > 0))
);


ALTER TABLE public.concepts OWNER TO mccoy;

--
-- Name: TABLE concepts; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON TABLE public.concepts IS 'Core gematria concepts with full metadata and book attribution';


--
-- Name: COLUMN concepts.book_id; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.concepts.book_id IS 'Foreign key to books table (REQUIRED for proper tracking)';


--
-- Name: COLUMN concepts.theological_category; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.concepts.theological_category IS 'One of: Person, Place, Event, Object, Concept, Law, Leadership';


--
-- Name: COLUMN concepts.validation_status; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.concepts.validation_status IS 'Whether gematria has been verified by dual scripts';


--
-- Name: COLUMN concepts.strong_number; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.concepts.strong_number IS 'Strong''s number for linking to bible.hebrew_entries';


--
-- Name: COLUMN concepts.verse_occurrence_count; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.concepts.verse_occurrence_count IS 'Total occurrences in bible_db verses (cached from verse_noun_occurrences)';


--
-- Name: COLUMN concepts.embedding; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.concepts.embedding IS '768-dim vector embedding matching bible.verses for semantic search';


--
-- Name: COLUMN concepts.doctrinal_tags; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.concepts.doctrinal_tags IS 'Theological doctrine tags: Covenant, Atonement, Grace, Judgment, etc.';


--
-- Name: COLUMN concepts.temporal_eras; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.concepts.temporal_eras IS 'Biblical eras: Patriarchal, Exodus, Monarchy, Exile, Post-Exile, NT';


--
-- Name: COLUMN concepts.spatial_contexts; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.concepts.spatial_contexts IS 'Geographic/spatial contexts: Temple, Wilderness, Jerusalem, etc.';


--
-- Name: COLUMN concepts.typological_links; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.concepts.typological_links IS 'JSONB array of typological connections to NT verses';


--
-- Name: COLUMN concepts.verse_occurrence_id; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.concepts.verse_occurrence_id IS 'Unique identifier for this specific occurrence of the noun in scripture. Format: {book}_{chapter}_{verse}_{noun_name}';


--
-- Name: COLUMN concepts.verse_context; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.concepts.verse_context IS 'The immediate textual context of this verse occurrence (1-2 surrounding verses)';


--
-- Name: COLUMN concepts.usage_context; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.concepts.usage_context IS 'How this noun is used in this specific verse - theological/narrative context specific to this occurrence';


--
-- Name: concepts_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.concepts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.concepts_id_seq OWNER TO mccoy;

--
-- Name: concepts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.concepts_id_seq OWNED BY public.concepts.id;


--
-- Name: confidence_validation_log; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.confidence_validation_log (
    id bigint NOT NULL,
    run_id uuid NOT NULL,
    node text NOT NULL,
    noun_id uuid NOT NULL,
    gematria_confidence numeric(5,4),
    ai_confidence numeric(5,4),
    gematria_threshold numeric(5,4),
    ai_threshold numeric(5,4),
    validation_passed boolean NOT NULL,
    abort_reason text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    CONSTRAINT confidence_validation_log_ai_confidence_check CHECK (((ai_confidence >= (0)::numeric) AND (ai_confidence <= (1)::numeric))),
    CONSTRAINT confidence_validation_log_ai_threshold_check CHECK (((ai_threshold >= (0)::numeric) AND (ai_threshold <= (1)::numeric))),
    CONSTRAINT confidence_validation_log_gematria_confidence_check CHECK (((gematria_confidence >= (0)::numeric) AND (gematria_confidence <= (1)::numeric))),
    CONSTRAINT confidence_validation_log_gematria_threshold_check CHECK (((gematria_threshold >= (0)::numeric) AND (gematria_threshold <= (1)::numeric)))
);


ALTER TABLE public.confidence_validation_log OWNER TO mccoy;

--
-- Name: confidence_validation_log_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.confidence_validation_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.confidence_validation_log_id_seq OWNER TO mccoy;

--
-- Name: confidence_validation_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.confidence_validation_log_id_seq OWNED BY public.confidence_validation_log.id;


--
-- Name: connections; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.connections (
    id integer NOT NULL,
    concept_a_id integer,
    concept_b_id integer,
    shared_factors integer[] NOT NULL,
    connection_strength integer NOT NULL,
    factor_product integer,
    connection_type character varying(50),
    theological_significance text,
    discovered_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT connections_check CHECK ((concept_a_id < concept_b_id))
);


ALTER TABLE public.connections OWNER TO mccoy;

--
-- Name: TABLE connections; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON TABLE public.connections IS 'Edges between concepts based on shared prime factors';


--
-- Name: connections_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.connections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.connections_id_seq OWNER TO mccoy;

--
-- Name: connections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.connections_id_seq OWNED BY public.connections.id;


--
-- Name: cross_references; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.cross_references (
    id integer NOT NULL,
    source_concept_id integer,
    target_concept_id integer,
    reference_type character varying(100) NOT NULL,
    description text,
    verse_link text,
    strength integer DEFAULT 1,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT cross_references_strength_check CHECK (((strength >= 1) AND (strength <= 5)))
);


ALTER TABLE public.cross_references OWNER TO mccoy;

--
-- Name: cross_references_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.cross_references_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cross_references_id_seq OWNER TO mccoy;

--
-- Name: cross_references_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.cross_references_id_seq OWNED BY public.cross_references.id;


--
-- Name: doctrinal_links; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.doctrinal_links (
    id integer NOT NULL,
    concept_id integer,
    bible_verse_id integer,
    link_type character varying(50),
    weight double precision DEFAULT 1.0,
    evidence text,
    nt_verse_ref character varying(100),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    validated boolean DEFAULT false,
    CONSTRAINT doctrinal_links_link_type_check CHECK (((link_type)::text = ANY ((ARRAY['typology'::character varying, 'prophecy'::character varying, 'contrast'::character varying, 'fulfillment'::character varying, 'parallel'::character varying])::text[]))),
    CONSTRAINT doctrinal_links_weight_check CHECK (((weight >= (0)::double precision) AND (weight <= (1)::double precision)))
);


ALTER TABLE public.doctrinal_links OWNER TO mccoy;

--
-- Name: TABLE doctrinal_links; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON TABLE public.doctrinal_links IS 'Typological and prophetic connections between OT concepts and NT fulfillments';


--
-- Name: COLUMN doctrinal_links.weight; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.doctrinal_links.weight IS 'Confidence score for the typological connection (0-1)';


--
-- Name: doctrinal_links_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.doctrinal_links_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.doctrinal_links_id_seq OWNER TO mccoy;

--
-- Name: doctrinal_links_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.doctrinal_links_id_seq OWNED BY public.doctrinal_links.id;


--
-- Name: hypotheses; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.hypotheses (
    id integer NOT NULL,
    hypothesis_number integer NOT NULL,
    title character varying(255) NOT NULL,
    description text NOT NULL,
    status character varying(50) DEFAULT 'proposed'::character varying,
    supporting_concepts integer[],
    supporting_evidence text,
    counter_evidence text,
    proposed_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_tested timestamp without time zone,
    proposed_by character varying(100),
    confidence_level integer,
    CONSTRAINT hypotheses_confidence_level_check CHECK (((confidence_level >= 1) AND (confidence_level <= 10))),
    CONSTRAINT hypotheses_status_check CHECK (((status)::text = ANY ((ARRAY['proposed'::character varying, 'supported'::character varying, 'refuted'::character varying, 'inconclusive'::character varying, 'modified'::character varying])::text[])))
);


ALTER TABLE public.hypotheses OWNER TO mccoy;

--
-- Name: hypotheses_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.hypotheses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.hypotheses_id_seq OWNER TO mccoy;

--
-- Name: hypotheses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.hypotheses_id_seq OWNED BY public.hypotheses.id;


--
-- Name: integration_log; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.integration_log (
    id integer NOT NULL,
    book_id integer,
    book_name character varying(100) NOT NULL,
    concepts_added integer NOT NULL,
    integration_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    integration_method character varying(50),
    network_size_before integer,
    network_size_after integer,
    edges_added integer,
    notes text
);


ALTER TABLE public.integration_log OWNER TO mccoy;

--
-- Name: TABLE integration_log; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON TABLE public.integration_log IS 'Audit trail of book integrations and network growth';


--
-- Name: integration_log_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.integration_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.integration_log_id_seq OWNER TO mccoy;

--
-- Name: integration_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.integration_log_id_seq OWNED BY public.integration_log.id;


--
-- Name: isolation_patterns; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.isolation_patterns (
    id integer NOT NULL,
    concept_id integer,
    is_prime_value boolean NOT NULL,
    degree_count integer NOT NULL,
    isolation_type character varying(50),
    theological_significance text,
    discovered_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.isolation_patterns OWNER TO mccoy;

--
-- Name: TABLE isolation_patterns; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON TABLE public.isolation_patterns IS 'Concepts with low/zero connectivity (primes, unique values)';


--
-- Name: isolated_concepts; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.isolated_concepts AS
 SELECT c.name,
    c.gematria_value,
    c.book_source,
    i.is_prime_value,
    i.degree_count,
    i.isolation_type,
    i.theological_significance
   FROM (public.concepts c
     JOIN public.isolation_patterns i ON ((c.id = i.concept_id)))
  ORDER BY i.degree_count, c.name;


ALTER VIEW public.isolated_concepts OWNER TO mccoy;

--
-- Name: isolation_patterns_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.isolation_patterns_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.isolation_patterns_id_seq OWNER TO mccoy;

--
-- Name: isolation_patterns_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.isolation_patterns_id_seq OWNED BY public.isolation_patterns.id;


--
-- Name: metrics_log; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.metrics_log (
    id bigint NOT NULL,
    run_id uuid NOT NULL,
    workflow text NOT NULL,
    thread_id text NOT NULL,
    node text NOT NULL,
    event text NOT NULL,
    status text NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    finished_at timestamp with time zone,
    duration_ms numeric,
    items_in integer,
    items_out integer,
    error_json jsonb,
    meta jsonb,
    CONSTRAINT metrics_log_event_check CHECK ((event = ANY (ARRAY['node_start'::text, 'node_end'::text, 'node_error'::text, 'pipeline_start'::text, 'pipeline_end'::text]))),
    CONSTRAINT metrics_log_status_check CHECK ((status = ANY (ARRAY['ok'::text, 'error'::text, 'skip'::text])))
);


ALTER TABLE public.metrics_log OWNER TO mccoy;

--
-- Name: metrics_log_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.metrics_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.metrics_log_id_seq OWNER TO mccoy;

--
-- Name: metrics_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.metrics_log_id_seq OWNED BY public.metrics_log.id;


--
-- Name: v_metrics_flat; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.v_metrics_flat AS
 SELECT id,
    run_id,
    workflow,
    thread_id,
    node,
    event,
    status,
    started_at,
    finished_at,
    (EXTRACT(epoch FROM (finished_at - started_at)) * 1000.0) AS duration_ms,
    COALESCE(items_in, 0) AS items_in,
    COALESCE(items_out, 0) AS items_out,
    error_json,
    meta
   FROM public.metrics_log;


ALTER VIEW public.v_metrics_flat OWNER TO mccoy;

--
-- Name: v_node_latency_7d; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.v_node_latency_7d AS
 SELECT node,
    count(*) AS calls,
    avg(duration_ms) AS avg_ms,
    percentile_cont((0.5)::double precision) WITHIN GROUP (ORDER BY ((duration_ms)::double precision)) AS p50_ms,
    percentile_cont((0.9)::double precision) WITHIN GROUP (ORDER BY ((duration_ms)::double precision)) AS p90_ms,
    percentile_cont((0.95)::double precision) WITHIN GROUP (ORDER BY ((duration_ms)::double precision)) AS p95_ms,
    percentile_cont((0.99)::double precision) WITHIN GROUP (ORDER BY ((duration_ms)::double precision)) AS p99_ms
   FROM public.v_metrics_flat
  WHERE ((event = 'node_end'::text) AND (started_at >= (now() - '7 days'::interval)))
  GROUP BY node
  ORDER BY node;


ALTER VIEW public.v_node_latency_7d OWNER TO mccoy;

--
-- Name: mv_node_latency_7d; Type: MATERIALIZED VIEW; Schema: public; Owner: mccoy
--

CREATE MATERIALIZED VIEW public.mv_node_latency_7d AS
 SELECT node,
    calls,
    avg_ms,
    p50_ms,
    p90_ms,
    p95_ms,
    p99_ms
   FROM public.v_node_latency_7d
  WITH NO DATA;


ALTER MATERIALIZED VIEW public.mv_node_latency_7d OWNER TO mccoy;

--
-- Name: network_metrics; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.network_metrics (
    id integer NOT NULL,
    concept_id integer,
    degree integer NOT NULL,
    degree_rank integer,
    betweenness_centrality double precision,
    closeness_centrality double precision,
    eigenvector_centrality double precision,
    pagerank double precision,
    component_id integer,
    component_size integer,
    is_isolated boolean DEFAULT false,
    snapshot_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    network_size integer,
    network_edges integer
);


ALTER TABLE public.network_metrics OWNER TO mccoy;

--
-- Name: TABLE network_metrics; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON TABLE public.network_metrics IS 'Calculated centrality measures and network statistics';


--
-- Name: COLUMN network_metrics.degree_rank; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.network_metrics.degree_rank IS '1 = highest degree (top hub), increments from there';


--
-- Name: network_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.network_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.network_metrics_id_seq OWNER TO mccoy;

--
-- Name: network_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.network_metrics_id_seq OWNED BY public.network_metrics.id;


--
-- Name: prime_factors; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.prime_factors (
    id integer NOT NULL,
    concept_id integer,
    prime_factor integer NOT NULL,
    exponent integer NOT NULL,
    is_unique boolean DEFAULT false,
    theological_meaning text,
    CONSTRAINT prime_factors_exponent_check CHECK ((exponent > 0)),
    CONSTRAINT prime_factors_prime_factor_check CHECK ((prime_factor > 1))
);


ALTER TABLE public.prime_factors OWNER TO mccoy;

--
-- Name: TABLE prime_factors; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON TABLE public.prime_factors IS 'Prime factorization breakdown for mathematical analysis';


--
-- Name: prime_factors_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.prime_factors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prime_factors_id_seq OWNER TO mccoy;

--
-- Name: prime_factors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.prime_factors_id_seq OWNED BY public.prime_factors.id;


--
-- Name: qwen_health_log; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.qwen_health_log (
    id bigint NOT NULL,
    run_id uuid NOT NULL,
    embedding_model text NOT NULL,
    reranker_model text NOT NULL,
    embed_dim integer,
    lat_ms_embed integer,
    lat_ms_rerank integer,
    verified boolean NOT NULL,
    reason text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.qwen_health_log OWNER TO mccoy;

--
-- Name: TABLE qwen_health_log; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON TABLE public.qwen_health_log IS 'Stores Qwen model health check results for production verification';


--
-- Name: COLUMN qwen_health_log.run_id; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.qwen_health_log.run_id IS 'Pipeline run ID this health check belongs to';


--
-- Name: COLUMN qwen_health_log.embedding_model; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.qwen_health_log.embedding_model IS 'Name of embedding model verified';


--
-- Name: COLUMN qwen_health_log.reranker_model; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.qwen_health_log.reranker_model IS 'Name of reranker model verified';


--
-- Name: COLUMN qwen_health_log.embed_dim; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.qwen_health_log.embed_dim IS 'Embedding dimension verified (should be 1024)';


--
-- Name: COLUMN qwen_health_log.lat_ms_embed; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.qwen_health_log.lat_ms_embed IS 'Latency in ms for embedding dry-run test';


--
-- Name: COLUMN qwen_health_log.lat_ms_rerank; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.qwen_health_log.lat_ms_rerank IS 'Latency in ms for reranker dry-run test';


--
-- Name: COLUMN qwen_health_log.verified; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.qwen_health_log.verified IS 'Whether health check passed';


--
-- Name: COLUMN qwen_health_log.reason; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.qwen_health_log.reason IS 'Human-readable result or failure reason';


--
-- Name: qwen_health_log_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.qwen_health_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.qwen_health_log_id_seq OWNER TO mccoy;

--
-- Name: qwen_health_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.qwen_health_log_id_seq OWNED BY public.qwen_health_log.id;


--
-- Name: recent_integrations; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.recent_integrations AS
 SELECT book_name,
    concepts_added,
    integration_date,
    integration_method,
    edges_added,
    network_size_after
   FROM public.integration_log il
  ORDER BY integration_date DESC
 LIMIT 20;


ALTER VIEW public.recent_integrations OWNER TO mccoy;

--
-- Name: top_hubs; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.top_hubs AS
 SELECT c.name,
    c.gematria_value,
    c.book_source,
    m.degree,
    m.degree_rank,
    m.betweenness_centrality
   FROM (public.concepts c
     JOIN public.network_metrics m ON ((c.id = m.concept_id)))
  WHERE (m.snapshot_date = ( SELECT max(network_metrics.snapshot_date) AS max
           FROM public.network_metrics))
  ORDER BY m.degree DESC
 LIMIT 50;


ALTER VIEW public.top_hubs OWNER TO mccoy;

--
-- Name: twin_patterns; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.twin_patterns (
    id integer NOT NULL,
    concept_a_id integer,
    concept_b_id integer,
    shared_value integer NOT NULL,
    shared_degree integer,
    pattern_type character varying(50),
    theological_significance text,
    discovered_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT twin_patterns_check CHECK ((concept_a_id < concept_b_id))
);


ALTER TABLE public.twin_patterns OWNER TO mccoy;

--
-- Name: TABLE twin_patterns; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON TABLE public.twin_patterns IS 'Concepts with identical values or connectivity patterns';


--
-- Name: twin_patterns_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.twin_patterns_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.twin_patterns_id_seq OWNER TO mccoy;

--
-- Name: twin_patterns_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.twin_patterns_id_seq OWNED BY public.twin_patterns.id;


--
-- Name: v_concept_network_health; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.v_concept_network_health AS
 SELECT count(*) AS node_ct,
    (avg(public.vector_dims(embedding)))::integer AS avg_dim,
    min(public.vector_dims(embedding)) AS min_dim,
    max(public.vector_dims(embedding)) AS max_dim,
    avg((embedding OPERATOR(public.<#>) embedding)) AS avg_self_l2,
    now() AS observed_at
   FROM public.concept_network;


ALTER VIEW public.v_concept_network_health OWNER TO mccoy;

--
-- Name: v_concept_relations_health; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.v_concept_relations_health AS
 SELECT (count(*))::integer AS edge_ct,
    COALESCE(avg(cosine), (0)::double precision) AS avg_cosine,
    (sum(((cosine >= (0.90)::double precision))::integer))::integer AS strong_edges,
    (sum((((cosine >= (0.75)::double precision) AND (cosine < (0.90)::double precision)))::integer))::integer AS weak_edges,
    COALESCE(avg(rerank_score), (0)::double precision) AS avg_rerank_score,
    (COALESCE(avg((decided_yes)::integer), (0)::numeric))::double precision AS rerank_yes_ratio
   FROM public.concept_relations;


ALTER VIEW public.v_concept_relations_health OWNER TO mccoy;

--
-- Name: verse_noun_occurrences; Type: TABLE; Schema: public; Owner: mccoy
--

CREATE TABLE public.verse_noun_occurrences (
    id integer NOT NULL,
    concept_id integer,
    bible_verse_id integer,
    bible_book_name character varying(50),
    bible_chapter integer,
    bible_verse_num integer,
    context_text text,
    occurrence_position integer,
    strong_number character varying(10),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.verse_noun_occurrences OWNER TO mccoy;

--
-- Name: TABLE verse_noun_occurrences; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON TABLE public.verse_noun_occurrences IS 'Links gematria concepts to bible_db verses for exhaustive occurrence tracking';


--
-- Name: COLUMN verse_noun_occurrences.bible_verse_id; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON COLUMN public.verse_noun_occurrences.bible_verse_id IS 'References bible.verses.verse_id (no FK constraint to keep bible_db read-only)';


--
-- Name: v_concepts_with_verses; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.v_concepts_with_verses AS
 SELECT c.id,
    c.name,
    c.gematria_value,
    c.hebrew_text,
    c.book_source,
    c.strong_number,
    c.verse_occurrence_count,
    c.doctrinal_tags,
    c.temporal_eras,
    nm.degree,
    nm.betweenness_centrality,
    count(DISTINCT vno.id) AS actual_occurrence_count,
    jsonb_agg(DISTINCT jsonb_build_object('verse_id', vno.bible_verse_id, 'ref', (((((vno.bible_book_name)::text || ' '::text) || vno.bible_chapter) || ':'::text) || vno.bible_verse_num), 'position', vno.occurrence_position) ORDER BY (jsonb_build_object('verse_id', vno.bible_verse_id, 'ref', (((((vno.bible_book_name)::text || ' '::text) || vno.bible_chapter) || ':'::text) || vno.bible_verse_num), 'position', vno.occurrence_position))) FILTER (WHERE (vno.id IS NOT NULL)) AS verses
   FROM ((public.concepts c
     LEFT JOIN public.network_metrics nm ON (((c.id = nm.concept_id) AND (nm.snapshot_date = ( SELECT max(network_metrics.snapshot_date) AS max
           FROM public.network_metrics)))))
     LEFT JOIN public.verse_noun_occurrences vno ON ((c.id = vno.concept_id)))
  GROUP BY c.id, c.name, c.gematria_value, c.hebrew_text, c.book_source, c.strong_number, c.verse_occurrence_count, c.doctrinal_tags, c.temporal_eras, nm.degree, nm.betweenness_centrality;


ALTER VIEW public.v_concepts_with_verses OWNER TO mccoy;

--
-- Name: VIEW v_concepts_with_verses; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON VIEW public.v_concepts_with_verses IS 'Enriched concept view with verse occurrence data and network metrics';


--
-- Name: v_doctrinal_connections; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.v_doctrinal_connections AS
 SELECT dl.id,
    dl.link_type,
    dl.evidence,
    dl.nt_verse_ref,
    c.name AS concept_name,
    c.gematria_value,
    c.hebrew_text,
    c.book_source,
    dl.bible_verse_id,
    dl.weight,
    dl.validated,
    dl.created_at
   FROM (public.doctrinal_links dl
     JOIN public.concepts c ON ((dl.concept_id = c.id)))
  ORDER BY dl.weight DESC, c.name;


ALTER VIEW public.v_doctrinal_connections OWNER TO mccoy;

--
-- Name: VIEW v_doctrinal_connections; Type: COMMENT; Schema: public; Owner: mccoy
--

COMMENT ON VIEW public.v_doctrinal_connections IS 'Typological and prophetic connections between OT gematria concepts and NT fulfillments';


--
-- Name: v_metrics_last_event; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.v_metrics_last_event AS
 SELECT DISTINCT ON (run_id, node) run_id,
    node,
    event,
    status,
    started_at,
    finished_at
   FROM public.metrics_log
  ORDER BY run_id, node, started_at DESC;


ALTER VIEW public.v_metrics_last_event OWNER TO mccoy;

--
-- Name: v_metrics_overview; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.v_metrics_overview AS
 SELECT (count(*))::integer AS node_ct,
    (( SELECT count(*) AS count
           FROM public.concept_relations))::integer AS edge_ct,
    (( SELECT count(DISTINCT concept_clusters.cluster_id) AS count
           FROM public.concept_clusters))::integer AS cluster_ct,
    COALESCE(( SELECT avg(cluster_metrics.density) AS avg
           FROM public.cluster_metrics), (0)::double precision) AS avg_cluster_density,
    COALESCE(( SELECT avg(cluster_metrics.semantic_diversity) AS avg
           FROM public.cluster_metrics), (0)::double precision) AS avg_cluster_diversity;


ALTER VIEW public.v_metrics_overview OWNER TO mccoy;

--
-- Name: v_node_throughput_24h; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.v_node_throughput_24h AS
 SELECT node,
    date_trunc('minute'::text, finished_at) AS minute,
    sum(items_out) AS items_out
   FROM public.v_metrics_flat
  WHERE ((event = 'node_end'::text) AND (finished_at >= (now() - '24:00:00'::interval)))
  GROUP BY node, (date_trunc('minute'::text, finished_at))
  ORDER BY (date_trunc('minute'::text, finished_at)) DESC, node;


ALTER VIEW public.v_node_throughput_24h OWNER TO mccoy;

--
-- Name: v_pipeline_runs; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.v_pipeline_runs AS
 WITH bounds AS (
         SELECT metrics_log.run_id,
            min(metrics_log.started_at) AS t0,
            max(COALESCE(metrics_log.finished_at, metrics_log.started_at)) AS t1
           FROM public.metrics_log
          GROUP BY metrics_log.run_id
        )
 SELECT run_id,
    t0 AS started_at,
    t1 AS finished_at,
    (EXTRACT(epoch FROM (t1 - t0)) * 1000.0) AS duration_ms
   FROM bounds b;


ALTER VIEW public.v_pipeline_runs OWNER TO mccoy;

--
-- Name: v_recent_errors_7d; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.v_recent_errors_7d AS
 SELECT node,
    count(*) AS error_count,
    max(finished_at) AS last_seen,
    jsonb_agg(DISTINCT (error_json ->> 'type'::text)) FILTER (WHERE (error_json IS NOT NULL)) AS error_types
   FROM public.v_metrics_flat
  WHERE ((event = 'node_error'::text) AND (started_at >= (now() - '7 days'::interval)))
  GROUP BY node
  ORDER BY (count(*)) DESC, (max(finished_at)) DESC;


ALTER VIEW public.v_recent_errors_7d OWNER TO mccoy;

--
-- Name: v_run_confidence_summary; Type: VIEW; Schema: public; Owner: mccoy
--

CREATE VIEW public.v_run_confidence_summary AS
 SELECT run_id,
    count(*) AS total_validations,
    avg(gematria_confidence) AS avg_gematria_confidence,
    avg(ai_confidence) AS avg_ai_confidence,
    sum(
        CASE
            WHEN validation_passed THEN 1
            ELSE 0
        END) AS passed_validations,
    sum(
        CASE
            WHEN (NOT validation_passed) THEN 1
            ELSE 0
        END) AS failed_validations,
    min(created_at) AS run_started_at,
    max(created_at) AS run_completed_at
   FROM public.confidence_validation_log
  GROUP BY run_id;


ALTER VIEW public.v_run_confidence_summary OWNER TO mccoy;

--
-- Name: verse_noun_occurrences_id_seq; Type: SEQUENCE; Schema: public; Owner: mccoy
--

CREATE SEQUENCE public.verse_noun_occurrences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.verse_noun_occurrences_id_seq OWNER TO mccoy;

--
-- Name: verse_noun_occurrences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: mccoy
--

ALTER SEQUENCE public.verse_noun_occurrences_id_seq OWNED BY public.verse_noun_occurrences.id;


--
-- Name: concept_network id; Type: DEFAULT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.concept_network ALTER COLUMN id SET DEFAULT nextval('gematria.concept_network_id_seq'::regclass);


--
-- Name: nouns id; Type: DEFAULT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.nouns ALTER COLUMN id SET DEFAULT nextval('gematria.nouns_id_seq'::regclass);


--
-- Name: ai_enrichment_log id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.ai_enrichment_log ALTER COLUMN id SET DEFAULT nextval('public.ai_enrichment_log_id_seq'::regclass);


--
-- Name: books id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.books ALTER COLUMN id SET DEFAULT nextval('public.books_id_seq'::regclass);


--
-- Name: concepts id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.concepts ALTER COLUMN id SET DEFAULT nextval('public.concepts_id_seq'::regclass);


--
-- Name: confidence_validation_log id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.confidence_validation_log ALTER COLUMN id SET DEFAULT nextval('public.confidence_validation_log_id_seq'::regclass);


--
-- Name: connections id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.connections ALTER COLUMN id SET DEFAULT nextval('public.connections_id_seq'::regclass);


--
-- Name: cross_references id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.cross_references ALTER COLUMN id SET DEFAULT nextval('public.cross_references_id_seq'::regclass);


--
-- Name: doctrinal_links id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.doctrinal_links ALTER COLUMN id SET DEFAULT nextval('public.doctrinal_links_id_seq'::regclass);


--
-- Name: hypotheses id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.hypotheses ALTER COLUMN id SET DEFAULT nextval('public.hypotheses_id_seq'::regclass);


--
-- Name: integration_log id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.integration_log ALTER COLUMN id SET DEFAULT nextval('public.integration_log_id_seq'::regclass);


--
-- Name: isolation_patterns id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.isolation_patterns ALTER COLUMN id SET DEFAULT nextval('public.isolation_patterns_id_seq'::regclass);


--
-- Name: metrics_log id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.metrics_log ALTER COLUMN id SET DEFAULT nextval('public.metrics_log_id_seq'::regclass);


--
-- Name: network_metrics id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.network_metrics ALTER COLUMN id SET DEFAULT nextval('public.network_metrics_id_seq'::regclass);


--
-- Name: prime_factors id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.prime_factors ALTER COLUMN id SET DEFAULT nextval('public.prime_factors_id_seq'::regclass);


--
-- Name: qwen_health_log id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.qwen_health_log ALTER COLUMN id SET DEFAULT nextval('public.qwen_health_log_id_seq'::regclass);


--
-- Name: twin_patterns id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.twin_patterns ALTER COLUMN id SET DEFAULT nextval('public.twin_patterns_id_seq'::regclass);


--
-- Name: verse_noun_occurrences id; Type: DEFAULT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.verse_noun_occurrences ALTER COLUMN id SET DEFAULT nextval('public.verse_noun_occurrences_id_seq'::regclass);


--
-- Name: concept_centrality concept_centrality_pkey; Type: CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.concept_centrality
    ADD CONSTRAINT concept_centrality_pkey PRIMARY KEY (concept_id);


--
-- Name: concept_clusters concept_clusters_pkey; Type: CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.concept_clusters
    ADD CONSTRAINT concept_clusters_pkey PRIMARY KEY (concept_id);


--
-- Name: concept_network concept_network_pkey; Type: CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.concept_network
    ADD CONSTRAINT concept_network_pkey PRIMARY KEY (id);


--
-- Name: concept_relations concept_relations_pkey; Type: CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.concept_relations
    ADD CONSTRAINT concept_relations_pkey PRIMARY KEY (relation_id);


--
-- Name: concepts concepts_content_hash_key; Type: CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.concepts
    ADD CONSTRAINT concepts_content_hash_key UNIQUE (content_hash);


--
-- Name: concepts concepts_pkey; Type: CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.concepts
    ADD CONSTRAINT concepts_pkey PRIMARY KEY (concept_id);


--
-- Name: noun_occurrences noun_occurrences_pkey; Type: CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.noun_occurrences
    ADD CONSTRAINT noun_occurrences_pkey PRIMARY KEY (noun_id, verse_id, token_idx);


--
-- Name: nouns nouns_lemma_key; Type: CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.nouns
    ADD CONSTRAINT nouns_lemma_key UNIQUE (lemma);


--
-- Name: nouns nouns_pkey; Type: CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.nouns
    ADD CONSTRAINT nouns_pkey PRIMARY KEY (id);


--
-- Name: ai_enrichment_log ai_enrichment_log_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.ai_enrichment_log
    ADD CONSTRAINT ai_enrichment_log_pkey PRIMARY KEY (id);


--
-- Name: books books_name_key; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_name_key UNIQUE (name);


--
-- Name: books books_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_pkey PRIMARY KEY (id);


--
-- Name: books books_testament_book_number_key; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.books
    ADD CONSTRAINT books_testament_book_number_key UNIQUE (testament, book_number);


--
-- Name: checkpointer_state checkpointer_state_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.checkpointer_state
    ADD CONSTRAINT checkpointer_state_pkey PRIMARY KEY (workflow, thread_id, checkpoint_id);


--
-- Name: checkpointer_writes checkpointer_writes_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.checkpointer_writes
    ADD CONSTRAINT checkpointer_writes_pkey PRIMARY KEY (workflow, thread_id, checkpoint_id, task_id, idx);


--
-- Name: cluster_metrics cluster_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.cluster_metrics
    ADD CONSTRAINT cluster_metrics_pkey PRIMARY KEY (cluster_id);


--
-- Name: concept_centrality concept_centrality_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.concept_centrality
    ADD CONSTRAINT concept_centrality_pkey PRIMARY KEY (concept_id);


--
-- Name: concept_clusters concept_clusters_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.concept_clusters
    ADD CONSTRAINT concept_clusters_pkey PRIMARY KEY (concept_id);


--
-- Name: concept_metadata concept_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.concept_metadata
    ADD CONSTRAINT concept_metadata_pkey PRIMARY KEY (concept_id);


--
-- Name: concept_metrics concept_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.concept_metrics
    ADD CONSTRAINT concept_metrics_pkey PRIMARY KEY (concept_id);


--
-- Name: concept_network concept_network_concept_id_unique; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.concept_network
    ADD CONSTRAINT concept_network_concept_id_unique UNIQUE (concept_id);


--
-- Name: concept_network concept_network_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.concept_network
    ADD CONSTRAINT concept_network_pkey PRIMARY KEY (id);


--
-- Name: concept_relations concept_relations_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.concept_relations
    ADD CONSTRAINT concept_relations_pkey PRIMARY KEY (id);


--
-- Name: concept_relations concept_relations_uniq; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.concept_relations
    ADD CONSTRAINT concept_relations_uniq UNIQUE (source_id, target_id);


--
-- Name: concept_rerank_cache concept_rerank_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.concept_rerank_cache
    ADD CONSTRAINT concept_rerank_cache_pkey PRIMARY KEY (source_id, target_id, model);


--
-- Name: concepts concepts_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.concepts
    ADD CONSTRAINT concepts_pkey PRIMARY KEY (id);


--
-- Name: confidence_validation_log confidence_validation_log_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.confidence_validation_log
    ADD CONSTRAINT confidence_validation_log_pkey PRIMARY KEY (id);


--
-- Name: connections connections_concept_a_id_concept_b_id_key; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.connections
    ADD CONSTRAINT connections_concept_a_id_concept_b_id_key UNIQUE (concept_a_id, concept_b_id);


--
-- Name: connections connections_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.connections
    ADD CONSTRAINT connections_pkey PRIMARY KEY (id);


--
-- Name: cross_references cross_references_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.cross_references
    ADD CONSTRAINT cross_references_pkey PRIMARY KEY (id);


--
-- Name: doctrinal_links doctrinal_links_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.doctrinal_links
    ADD CONSTRAINT doctrinal_links_pkey PRIMARY KEY (id);


--
-- Name: hypotheses hypotheses_hypothesis_number_key; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.hypotheses
    ADD CONSTRAINT hypotheses_hypothesis_number_key UNIQUE (hypothesis_number);


--
-- Name: hypotheses hypotheses_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.hypotheses
    ADD CONSTRAINT hypotheses_pkey PRIMARY KEY (id);


--
-- Name: integration_log integration_log_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.integration_log
    ADD CONSTRAINT integration_log_pkey PRIMARY KEY (id);


--
-- Name: isolation_patterns isolation_patterns_concept_id_key; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.isolation_patterns
    ADD CONSTRAINT isolation_patterns_concept_id_key UNIQUE (concept_id);


--
-- Name: isolation_patterns isolation_patterns_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.isolation_patterns
    ADD CONSTRAINT isolation_patterns_pkey PRIMARY KEY (id);


--
-- Name: metrics_log metrics_log_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.metrics_log
    ADD CONSTRAINT metrics_log_pkey PRIMARY KEY (id);


--
-- Name: network_metrics network_metrics_concept_id_snapshot_date_key; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.network_metrics
    ADD CONSTRAINT network_metrics_concept_id_snapshot_date_key UNIQUE (concept_id, snapshot_date);


--
-- Name: network_metrics network_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.network_metrics
    ADD CONSTRAINT network_metrics_pkey PRIMARY KEY (id);


--
-- Name: prime_factors prime_factors_concept_id_prime_factor_key; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.prime_factors
    ADD CONSTRAINT prime_factors_concept_id_prime_factor_key UNIQUE (concept_id, prime_factor);


--
-- Name: prime_factors prime_factors_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.prime_factors
    ADD CONSTRAINT prime_factors_pkey PRIMARY KEY (id);


--
-- Name: qwen_health_log qwen_health_log_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.qwen_health_log
    ADD CONSTRAINT qwen_health_log_pkey PRIMARY KEY (id);


--
-- Name: twin_patterns twin_patterns_concept_a_id_concept_b_id_key; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.twin_patterns
    ADD CONSTRAINT twin_patterns_concept_a_id_concept_b_id_key UNIQUE (concept_a_id, concept_b_id);


--
-- Name: twin_patterns twin_patterns_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.twin_patterns
    ADD CONSTRAINT twin_patterns_pkey PRIMARY KEY (id);


--
-- Name: verse_noun_occurrences verse_noun_occurrences_pkey; Type: CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.verse_noun_occurrences
    ADD CONSTRAINT verse_noun_occurrences_pkey PRIMARY KEY (id);


--
-- Name: idx_concept_clusters_cluster_id; Type: INDEX; Schema: gematria; Owner: mccoy
--

CREATE INDEX idx_concept_clusters_cluster_id ON gematria.concept_clusters USING btree (cluster_id);


--
-- Name: idx_concept_network_concept_id; Type: INDEX; Schema: gematria; Owner: mccoy
--

CREATE INDEX idx_concept_network_concept_id ON gematria.concept_network USING btree (concept_id);


--
-- Name: idx_concepts_gematria; Type: INDEX; Schema: gematria; Owner: mccoy
--

CREATE INDEX idx_concepts_gematria ON gematria.concepts USING btree (gematria_value);


--
-- Name: idx_concepts_hash; Type: INDEX; Schema: gematria; Owner: mccoy
--

CREATE INDEX idx_concepts_hash ON gematria.concepts USING btree (content_hash);


--
-- Name: idx_concepts_name; Type: INDEX; Schema: gematria; Owner: mccoy
--

CREATE INDEX idx_concepts_name ON gematria.concepts USING btree (name);


--
-- Name: idx_noun_occurrences_verse_id; Type: INDEX; Schema: gematria; Owner: mccoy
--

CREATE INDEX idx_noun_occurrences_verse_id ON gematria.noun_occurrences USING btree (verse_id);


--
-- Name: idx_nouns_lemma; Type: INDEX; Schema: gematria; Owner: mccoy
--

CREATE INDEX idx_nouns_lemma ON gematria.nouns USING btree (lemma);


--
-- Name: idx_relations_dst; Type: INDEX; Schema: gematria; Owner: mccoy
--

CREATE INDEX idx_relations_dst ON gematria.concept_relations USING btree (dst_concept_id);


--
-- Name: idx_relations_src; Type: INDEX; Schema: gematria; Owner: mccoy
--

CREATE INDEX idx_relations_src ON gematria.concept_relations USING btree (src_concept_id);


--
-- Name: idx_relations_type; Type: INDEX; Schema: gematria; Owner: mccoy
--

CREATE INDEX idx_relations_type ON gematria.concept_relations USING btree (relation_type);


--
-- Name: uq_relations_src_dst_type; Type: INDEX; Schema: gematria; Owner: mccoy
--

CREATE UNIQUE INDEX uq_relations_src_dst_type ON gematria.concept_relations USING btree (src_concept_id, dst_concept_id, relation_type);


--
-- Name: ai_enrichment_node_idx; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX ai_enrichment_node_idx ON public.ai_enrichment_log USING btree (node);


--
-- Name: ai_enrichment_run_idx; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX ai_enrichment_run_idx ON public.ai_enrichment_log USING btree (run_id);


--
-- Name: concepts_name_verse_unique; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE UNIQUE INDEX concepts_name_verse_unique ON public.concepts USING btree (name, primary_verse);


--
-- Name: confidence_validation_node_idx; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX confidence_validation_node_idx ON public.confidence_validation_log USING btree (node);


--
-- Name: confidence_validation_passed_idx; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX confidence_validation_passed_idx ON public.confidence_validation_log USING btree (validation_passed);


--
-- Name: confidence_validation_run_idx; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX confidence_validation_run_idx ON public.confidence_validation_log USING btree (run_id);


--
-- Name: idx_books_category; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_books_category ON public.books USING btree (category);


--
-- Name: idx_books_number; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_books_number ON public.books USING btree (book_number);


--
-- Name: idx_books_status; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_books_status ON public.books USING btree (integration_status);


--
-- Name: idx_books_testament; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_books_testament ON public.books USING btree (testament);


--
-- Name: idx_checkpointer_state_workflow_thread_created; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_checkpointer_state_workflow_thread_created ON public.checkpointer_state USING btree (workflow, thread_id, created_at DESC);


--
-- Name: idx_cn_bge_m3_hnsw; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_cn_bge_m3_hnsw ON public.concept_network USING hnsw (embedding_bge_m3 public.vector_cosine_ops);


--
-- Name: idx_cn_qwen3_hnsw; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_cn_qwen3_hnsw ON public.concept_network USING hnsw (embedding public.vector_cosine_ops);


--
-- Name: idx_concept_metadata_label; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concept_metadata_label ON public.concept_metadata USING btree (label);


--
-- Name: idx_concept_metadata_source; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concept_metadata_source ON public.concept_metadata USING btree (source);


--
-- Name: idx_concept_network_concept_id; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concept_network_concept_id ON public.concept_network USING btree (concept_id);


--
-- Name: idx_concept_network_embedding; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concept_network_embedding ON public.concept_network USING ivfflat (embedding public.vector_cosine_ops) WITH (lists='100');


--
-- Name: idx_concept_relations_pair; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concept_relations_pair ON public.concept_relations USING btree (source_id, target_id);


--
-- Name: idx_concept_relations_similarity; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concept_relations_similarity ON public.concept_relations USING btree (similarity DESC);


--
-- Name: idx_concept_relations_type; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concept_relations_type ON public.concept_relations USING btree (relation_type);


--
-- Name: idx_concepts_book; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concepts_book ON public.concepts USING btree (book_source);


--
-- Name: idx_concepts_book_id; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concepts_book_id ON public.concepts USING btree (book_id);


--
-- Name: idx_concepts_category; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concepts_category ON public.concepts USING btree (theological_category);


--
-- Name: idx_concepts_doctrinal; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concepts_doctrinal ON public.concepts USING gin (doctrinal_tags);


--
-- Name: idx_concepts_embedding; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concepts_embedding ON public.concepts USING hnsw (embedding public.vector_cosine_ops) WHERE (embedding IS NOT NULL);


--
-- Name: idx_concepts_spatial; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concepts_spatial ON public.concepts USING gin (spatial_contexts);


--
-- Name: idx_concepts_strong; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concepts_strong ON public.concepts USING btree (strong_number);


--
-- Name: idx_concepts_tags; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concepts_tags ON public.concepts USING gin (semantic_tags);


--
-- Name: idx_concepts_temporal; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concepts_temporal ON public.concepts USING gin (temporal_eras);


--
-- Name: idx_concepts_validation; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concepts_validation ON public.concepts USING btree (validation_status);


--
-- Name: idx_concepts_value; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concepts_value ON public.concepts USING btree (gematria_value);


--
-- Name: idx_concepts_verse_occurrence; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_concepts_verse_occurrence ON public.concepts USING btree (verse_occurrence_id);


--
-- Name: idx_connections_concept_a; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_connections_concept_a ON public.connections USING btree (concept_a_id);


--
-- Name: idx_connections_concept_b; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_connections_concept_b ON public.connections USING btree (concept_b_id);


--
-- Name: idx_connections_strength; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_connections_strength ON public.connections USING btree (connection_strength DESC);


--
-- Name: idx_doctrinal_concept; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_doctrinal_concept ON public.doctrinal_links USING btree (concept_id);


--
-- Name: idx_doctrinal_type; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_doctrinal_type ON public.doctrinal_links USING btree (link_type);


--
-- Name: idx_doctrinal_validated; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_doctrinal_validated ON public.doctrinal_links USING btree (validated);


--
-- Name: idx_doctrinal_verse; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_doctrinal_verse ON public.doctrinal_links USING btree (bible_verse_id);


--
-- Name: idx_factors_concept; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_factors_concept ON public.prime_factors USING btree (concept_id);


--
-- Name: idx_factors_prime; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_factors_prime ON public.prime_factors USING btree (prime_factor);


--
-- Name: idx_metrics_degree; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_metrics_degree ON public.network_metrics USING btree (degree DESC);


--
-- Name: idx_metrics_isolated; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_metrics_isolated ON public.network_metrics USING btree (is_isolated);


--
-- Name: idx_metrics_rank; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_metrics_rank ON public.network_metrics USING btree (degree_rank);


--
-- Name: idx_qwen_health_log_created_at; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_qwen_health_log_created_at ON public.qwen_health_log USING btree (created_at DESC);


--
-- Name: idx_qwen_health_log_run_id; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_qwen_health_log_run_id ON public.qwen_health_log USING btree (run_id);


--
-- Name: idx_qwen_health_log_verified; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_qwen_health_log_verified ON public.qwen_health_log USING btree (verified);


--
-- Name: idx_verse_noun_bible; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_verse_noun_bible ON public.verse_noun_occurrences USING btree (bible_verse_id);


--
-- Name: idx_verse_noun_book; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_verse_noun_book ON public.verse_noun_occurrences USING btree (bible_book_name);


--
-- Name: idx_verse_noun_concept; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_verse_noun_concept ON public.verse_noun_occurrences USING btree (concept_id);


--
-- Name: idx_verse_noun_strongs; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX idx_verse_noun_strongs ON public.verse_noun_occurrences USING btree (strong_number);


--
-- Name: metrics_log_event_idx; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX metrics_log_event_idx ON public.metrics_log USING btree (event, started_at DESC);


--
-- Name: metrics_log_node_idx; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX metrics_log_node_idx ON public.metrics_log USING btree (node, started_at DESC);


--
-- Name: metrics_log_run_idx; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX metrics_log_run_idx ON public.metrics_log USING btree (run_id);


--
-- Name: metrics_log_thread_idx; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX metrics_log_thread_idx ON public.metrics_log USING btree (thread_id);


--
-- Name: metrics_log_workflow_ts; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX metrics_log_workflow_ts ON public.metrics_log USING btree (workflow, started_at DESC);


--
-- Name: mv_node_latency_7d_node_idx; Type: INDEX; Schema: public; Owner: mccoy
--

CREATE INDEX mv_node_latency_7d_node_idx ON public.mv_node_latency_7d USING btree (node);


--
-- Name: books_summary _RETURN; Type: RULE; Schema: public; Owner: mccoy
--

CREATE OR REPLACE VIEW public.books_summary AS
 SELECT b.id,
    b.name,
    b.hebrew_name,
    b.testament,
    b.category,
    b.book_number,
    b.concept_count,
    count(c.id) AS actual_concept_count,
    b.integration_status,
    b.integration_date,
    b.analysis_file
   FROM (public.books b
     LEFT JOIN public.concepts c ON ((b.id = c.book_id)))
  GROUP BY b.id
  ORDER BY b.book_number;


--
-- Name: concept_metadata trig_concept_metadata_updated_at; Type: TRIGGER; Schema: public; Owner: mccoy
--

CREATE TRIGGER trig_concept_metadata_updated_at BEFORE UPDATE ON public.concept_metadata FOR EACH ROW EXECUTE FUNCTION public.update_concept_metadata_updated_at();


--
-- Name: concepts trigger_concepts_updated_at; Type: TRIGGER; Schema: public; Owner: mccoy
--

CREATE TRIGGER trigger_concepts_updated_at BEFORE UPDATE ON public.concepts FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: concepts trigger_update_book_count; Type: TRIGGER; Schema: public; Owner: mccoy
--

CREATE TRIGGER trigger_update_book_count AFTER INSERT OR DELETE OR UPDATE ON public.concepts FOR EACH ROW EXECUTE FUNCTION public.update_book_concept_count();


--
-- Name: concept_centrality concept_centrality_concept_id_fkey; Type: FK CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.concept_centrality
    ADD CONSTRAINT concept_centrality_concept_id_fkey FOREIGN KEY (concept_id) REFERENCES gematria.concepts(concept_id) ON DELETE CASCADE;


--
-- Name: concept_clusters concept_clusters_concept_id_fkey; Type: FK CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.concept_clusters
    ADD CONSTRAINT concept_clusters_concept_id_fkey FOREIGN KEY (concept_id) REFERENCES gematria.concepts(concept_id);


--
-- Name: concept_network concept_network_concept_id_fkey; Type: FK CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.concept_network
    ADD CONSTRAINT concept_network_concept_id_fkey FOREIGN KEY (concept_id) REFERENCES gematria.concepts(concept_id);


--
-- Name: concept_relations concept_relations_dst_concept_id_fkey; Type: FK CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.concept_relations
    ADD CONSTRAINT concept_relations_dst_concept_id_fkey FOREIGN KEY (dst_concept_id) REFERENCES gematria.concepts(concept_id) ON DELETE CASCADE;


--
-- Name: concept_relations concept_relations_src_concept_id_fkey; Type: FK CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.concept_relations
    ADD CONSTRAINT concept_relations_src_concept_id_fkey FOREIGN KEY (src_concept_id) REFERENCES gematria.concepts(concept_id) ON DELETE CASCADE;


--
-- Name: noun_occurrences noun_occurrences_noun_id_fkey; Type: FK CONSTRAINT; Schema: gematria; Owner: mccoy
--

ALTER TABLE ONLY gematria.noun_occurrences
    ADD CONSTRAINT noun_occurrences_noun_id_fkey FOREIGN KEY (noun_id) REFERENCES gematria.nouns(id) ON DELETE CASCADE;


--
-- Name: concepts concepts_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.concepts
    ADD CONSTRAINT concepts_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id) ON DELETE SET NULL;


--
-- Name: connections connections_concept_a_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.connections
    ADD CONSTRAINT connections_concept_a_id_fkey FOREIGN KEY (concept_a_id) REFERENCES public.concepts(id) ON DELETE CASCADE;


--
-- Name: connections connections_concept_b_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.connections
    ADD CONSTRAINT connections_concept_b_id_fkey FOREIGN KEY (concept_b_id) REFERENCES public.concepts(id) ON DELETE CASCADE;


--
-- Name: cross_references cross_references_source_concept_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.cross_references
    ADD CONSTRAINT cross_references_source_concept_id_fkey FOREIGN KEY (source_concept_id) REFERENCES public.concepts(id) ON DELETE CASCADE;


--
-- Name: cross_references cross_references_target_concept_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.cross_references
    ADD CONSTRAINT cross_references_target_concept_id_fkey FOREIGN KEY (target_concept_id) REFERENCES public.concepts(id) ON DELETE CASCADE;


--
-- Name: doctrinal_links doctrinal_links_concept_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.doctrinal_links
    ADD CONSTRAINT doctrinal_links_concept_id_fkey FOREIGN KEY (concept_id) REFERENCES public.concepts(id) ON DELETE CASCADE;


--
-- Name: integration_log integration_log_book_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.integration_log
    ADD CONSTRAINT integration_log_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.books(id) ON DELETE SET NULL;


--
-- Name: isolation_patterns isolation_patterns_concept_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.isolation_patterns
    ADD CONSTRAINT isolation_patterns_concept_id_fkey FOREIGN KEY (concept_id) REFERENCES public.concepts(id) ON DELETE CASCADE;


--
-- Name: network_metrics network_metrics_concept_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.network_metrics
    ADD CONSTRAINT network_metrics_concept_id_fkey FOREIGN KEY (concept_id) REFERENCES public.concepts(id) ON DELETE CASCADE;


--
-- Name: prime_factors prime_factors_concept_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.prime_factors
    ADD CONSTRAINT prime_factors_concept_id_fkey FOREIGN KEY (concept_id) REFERENCES public.concepts(id) ON DELETE CASCADE;


--
-- Name: twin_patterns twin_patterns_concept_a_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.twin_patterns
    ADD CONSTRAINT twin_patterns_concept_a_id_fkey FOREIGN KEY (concept_a_id) REFERENCES public.concepts(id) ON DELETE CASCADE;


--
-- Name: twin_patterns twin_patterns_concept_b_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.twin_patterns
    ADD CONSTRAINT twin_patterns_concept_b_id_fkey FOREIGN KEY (concept_b_id) REFERENCES public.concepts(id) ON DELETE CASCADE;


--
-- Name: verse_noun_occurrences verse_noun_occurrences_concept_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: mccoy
--

ALTER TABLE ONLY public.verse_noun_occurrences
    ADD CONSTRAINT verse_noun_occurrences_concept_id_fkey FOREIGN KEY (concept_id) REFERENCES public.concepts(id) ON DELETE CASCADE;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: mccoy
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


--
-- PostgreSQL database dump complete
--

\unrestrict VU1XxeL3sy2r61aywhnBdThL1lbZKgXccesTVwRY7evw6yg8vaDyoW9HaBbSEMP

