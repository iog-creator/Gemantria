--
-- PostgreSQL database dump
--

-- Dumped from database version 16.6
-- Dumped by pg_dump version 16.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: bible; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA bible;


ALTER SCHEMA bible OWNER TO postgres;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: book_abbreviations; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.book_abbreviations (
    id integer NOT NULL,
    book_name character varying(50),
    abbreviation character varying(50) NOT NULL,
    source character varying(20),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE bible.book_abbreviations OWNER TO postgres;

--
-- Name: book_abbreviations_id_seq; Type: SEQUENCE; Schema: bible; Owner: postgres
--

CREATE SEQUENCE bible.book_abbreviations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE bible.book_abbreviations_id_seq OWNER TO postgres;

--
-- Name: book_abbreviations_id_seq; Type: SEQUENCE OWNED BY; Schema: bible; Owner: postgres
--

ALTER SEQUENCE bible.book_abbreviations_id_seq OWNED BY bible.book_abbreviations.id;


--
-- Name: books; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.books (
    book_id integer NOT NULL,
    name character varying(50) NOT NULL,
    testament character(2),
    chapters integer NOT NULL,
    CONSTRAINT books_testament_check CHECK ((testament = ANY (ARRAY['OT'::bpchar, 'NT'::bpchar])))
);


ALTER TABLE bible.books OWNER TO postgres;

--
-- Name: books_book_id_seq; Type: SEQUENCE; Schema: bible; Owner: postgres
--

CREATE SEQUENCE bible.books_book_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE bible.books_book_id_seq OWNER TO postgres;

--
-- Name: books_book_id_seq; Type: SEQUENCE OWNED BY; Schema: bible; Owner: postgres
--

ALTER SEQUENCE bible.books_book_id_seq OWNED BY bible.books.book_id;


--
-- Name: greek_entries; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.greek_entries (
    entry_id integer NOT NULL,
    strongs_id character varying(128) NOT NULL,
    lemma character varying(256) NOT NULL,
    transliteration character varying(100),
    definition text,
    usage text,
    gloss text
);


ALTER TABLE bible.greek_entries OWNER TO postgres;

--
-- Name: greek_entries_entry_id_seq; Type: SEQUENCE; Schema: bible; Owner: postgres
--

CREATE SEQUENCE bible.greek_entries_entry_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE bible.greek_entries_entry_id_seq OWNER TO postgres;

--
-- Name: greek_entries_entry_id_seq; Type: SEQUENCE OWNED BY; Schema: bible; Owner: postgres
--

ALTER SEQUENCE bible.greek_entries_entry_id_seq OWNED BY bible.greek_entries.entry_id;


--
-- Name: greek_morphology_codes; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.greek_morphology_codes (
    code character varying(256) NOT NULL,
    description text NOT NULL,
    part_of_speech character varying(512),
    morphology_type character varying(256),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE bible.greek_morphology_codes OWNER TO postgres;

--
-- Name: greek_nt_words; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.greek_nt_words (
    word_id integer NOT NULL,
    verse_id integer,
    word_position integer NOT NULL,
    word_text character varying(100) NOT NULL,
    strongs_id character varying(10),
    grammar_code character varying(50),
    transliteration character varying(100),
    gloss character varying(100),
    theological_term character varying(100)
);


ALTER TABLE bible.greek_nt_words OWNER TO postgres;

--
-- Name: greek_nt_words_word_id_seq; Type: SEQUENCE; Schema: bible; Owner: postgres
--

CREATE SEQUENCE bible.greek_nt_words_word_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE bible.greek_nt_words_word_id_seq OWNER TO postgres;

--
-- Name: greek_nt_words_word_id_seq; Type: SEQUENCE OWNED BY; Schema: bible; Owner: postgres
--

ALTER SEQUENCE bible.greek_nt_words_word_id_seq OWNED BY bible.greek_nt_words.word_id;


--
-- Name: hebrew_entries; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.hebrew_entries (
    entry_id integer NOT NULL,
    strongs_id character varying(128) NOT NULL,
    lemma character varying(50) NOT NULL,
    transliteration character varying(100),
    definition text,
    usage text,
    gloss text
);


ALTER TABLE bible.hebrew_entries OWNER TO postgres;

--
-- Name: hebrew_entries_entry_id_seq; Type: SEQUENCE; Schema: bible; Owner: postgres
--

CREATE SEQUENCE bible.hebrew_entries_entry_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE bible.hebrew_entries_entry_id_seq OWNER TO postgres;

--
-- Name: hebrew_entries_entry_id_seq; Type: SEQUENCE OWNED BY; Schema: bible; Owner: postgres
--

ALTER SEQUENCE bible.hebrew_entries_entry_id_seq OWNED BY bible.hebrew_entries.entry_id;


--
-- Name: hebrew_morphology_codes; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.hebrew_morphology_codes (
    code character varying(256) NOT NULL,
    description text NOT NULL,
    part_of_speech character varying(512),
    morphology_type character varying(256),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE bible.hebrew_morphology_codes OWNER TO postgres;

--
-- Name: hebrew_ot_words; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.hebrew_ot_words (
    word_id integer NOT NULL,
    verse_id integer,
    word_position integer NOT NULL,
    word_text character varying(100) NOT NULL,
    strongs_id character varying(10),
    grammar_code character varying(50),
    transliteration character varying(100),
    gloss character varying(100),
    theological_term character varying(100)
);


ALTER TABLE bible.hebrew_ot_words OWNER TO postgres;

--
-- Name: hebrew_ot_words_word_id_seq; Type: SEQUENCE; Schema: bible; Owner: postgres
--

CREATE SEQUENCE bible.hebrew_ot_words_word_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE bible.hebrew_ot_words_word_id_seq OWNER TO postgres;

--
-- Name: hebrew_ot_words_word_id_seq; Type: SEQUENCE OWNED BY; Schema: bible; Owner: postgres
--

ALTER SEQUENCE bible.hebrew_ot_words_word_id_seq OWNED BY bible.hebrew_ot_words.word_id;


--
-- Name: proper_names; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.proper_names (
    unified_name text,
    description text,
    parents text,
    siblings text,
    partners text,
    offspring text,
    tribe_nation text,
    summary text,
    type text,
    briefest text,
    brief text,
    short text,
    article text,
    category text
);


ALTER TABLE bible.proper_names OWNER TO postgres;

--
-- Name: tahot_verses_staging; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.tahot_verses_staging (
    book_id character varying(10),
    chapter integer,
    verse integer,
    text text
);


ALTER TABLE bible.tahot_verses_staging OWNER TO postgres;

--
-- Name: verse_embeddings; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.verse_embeddings (
    id integer NOT NULL,
    verse_id integer NOT NULL,
    book_name character varying(50) NOT NULL,
    chapter_num integer NOT NULL,
    verse_num integer NOT NULL,
    translation_source character varying(20) NOT NULL,
    embedding public.vector(1024) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE bible.verse_embeddings OWNER TO postgres;

--
-- Name: verse_embeddings_id_seq; Type: SEQUENCE; Schema: bible; Owner: postgres
--

CREATE SEQUENCE bible.verse_embeddings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE bible.verse_embeddings_id_seq OWNER TO postgres;

--
-- Name: verse_embeddings_id_seq; Type: SEQUENCE OWNED BY; Schema: bible; Owner: postgres
--

ALTER SEQUENCE bible.verse_embeddings_id_seq OWNED BY bible.verse_embeddings.id;


--
-- Name: verse_word_links; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.verse_word_links (
    id integer NOT NULL,
    verse_id integer NOT NULL,
    word_id integer NOT NULL,
    word_type text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE bible.verse_word_links OWNER TO postgres;

--
-- Name: verse_word_links_id_seq; Type: SEQUENCE; Schema: bible; Owner: postgres
--

CREATE SEQUENCE bible.verse_word_links_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE bible.verse_word_links_id_seq OWNER TO postgres;

--
-- Name: verse_word_links_id_seq; Type: SEQUENCE OWNED BY; Schema: bible; Owner: postgres
--

ALTER SEQUENCE bible.verse_word_links_id_seq OWNED BY bible.verse_word_links.id;


--
-- Name: verses; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.verses (
    verse_id integer NOT NULL,
    book_name character varying(50),
    chapter_num integer NOT NULL,
    verse_num integer NOT NULL,
    text text NOT NULL,
    translation_source character varying(10) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    embedding public.vector(768)
);


ALTER TABLE bible.verses OWNER TO postgres;

--
-- Name: verses_verse_id_seq; Type: SEQUENCE; Schema: bible; Owner: postgres
--

CREATE SEQUENCE bible.verses_verse_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE bible.verses_verse_id_seq OWNER TO postgres;

--
-- Name: verses_verse_id_seq; Type: SEQUENCE OWNED BY; Schema: bible; Owner: postgres
--

ALTER SEQUENCE bible.verses_verse_id_seq OWNED BY bible.verses.verse_id;


--
-- Name: versification_mappings; Type: TABLE; Schema: bible; Owner: postgres
--

CREATE TABLE bible.versification_mappings (
    mapping_id integer NOT NULL,
    source_tradition character varying(50) NOT NULL,
    source_book character varying(50),
    source_chapter character varying(10),
    source_verse character varying(10),
    target_tradition character varying(50) NOT NULL,
    target_book character varying(50),
    target_chapter character varying(10),
    target_verse character varying(10),
    mapping_type character varying(20),
    source_ref character varying(50),
    target_ref character varying(50),
    category character varying(10),
    notes text,
    source_subverse character varying(10),
    target_subverse character varying(10),
    note_a text,
    note_b text,
    ancient_versions text,
    test_conditions text
);


ALTER TABLE bible.versification_mappings OWNER TO postgres;

--
-- Name: versification_mappings_mapping_id_seq; Type: SEQUENCE; Schema: bible; Owner: postgres
--

CREATE SEQUENCE bible.versification_mappings_mapping_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE bible.versification_mappings_mapping_id_seq OWNER TO postgres;

--
-- Name: versification_mappings_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: bible; Owner: postgres
--

ALTER SEQUENCE bible.versification_mappings_mapping_id_seq OWNED BY bible.versification_mappings.mapping_id;


--
-- Name: langchain_pg_collection; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.langchain_pg_collection (
    uuid uuid NOT NULL,
    name character varying NOT NULL,
    cmetadata json
);


ALTER TABLE public.langchain_pg_collection OWNER TO postgres;

--
-- Name: langchain_pg_embedding; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.langchain_pg_embedding (
    id character varying NOT NULL,
    collection_id uuid,
    embedding public.vector(1024),
    document character varying,
    cmetadata jsonb
);


ALTER TABLE public.langchain_pg_embedding OWNER TO postgres;

--
-- Name: book_abbreviations id; Type: DEFAULT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.book_abbreviations ALTER COLUMN id SET DEFAULT nextval('bible.book_abbreviations_id_seq'::regclass);


--
-- Name: books book_id; Type: DEFAULT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.books ALTER COLUMN book_id SET DEFAULT nextval('bible.books_book_id_seq'::regclass);


--
-- Name: greek_entries entry_id; Type: DEFAULT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.greek_entries ALTER COLUMN entry_id SET DEFAULT nextval('bible.greek_entries_entry_id_seq'::regclass);


--
-- Name: greek_nt_words word_id; Type: DEFAULT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.greek_nt_words ALTER COLUMN word_id SET DEFAULT nextval('bible.greek_nt_words_word_id_seq'::regclass);


--
-- Name: hebrew_entries entry_id; Type: DEFAULT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.hebrew_entries ALTER COLUMN entry_id SET DEFAULT nextval('bible.hebrew_entries_entry_id_seq'::regclass);


--
-- Name: hebrew_ot_words word_id; Type: DEFAULT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.hebrew_ot_words ALTER COLUMN word_id SET DEFAULT nextval('bible.hebrew_ot_words_word_id_seq'::regclass);


--
-- Name: verse_embeddings id; Type: DEFAULT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verse_embeddings ALTER COLUMN id SET DEFAULT nextval('bible.verse_embeddings_id_seq'::regclass);


--
-- Name: verse_word_links id; Type: DEFAULT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verse_word_links ALTER COLUMN id SET DEFAULT nextval('bible.verse_word_links_id_seq'::regclass);


--
-- Name: verses verse_id; Type: DEFAULT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verses ALTER COLUMN verse_id SET DEFAULT nextval('bible.verses_verse_id_seq'::regclass);


--
-- Name: versification_mappings mapping_id; Type: DEFAULT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.versification_mappings ALTER COLUMN mapping_id SET DEFAULT nextval('bible.versification_mappings_mapping_id_seq'::regclass);


--
-- Name: book_abbreviations book_abbreviations_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.book_abbreviations
    ADD CONSTRAINT book_abbreviations_pkey PRIMARY KEY (id);


--
-- Name: books books_name_key; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.books
    ADD CONSTRAINT books_name_key UNIQUE (name);


--
-- Name: books books_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.books
    ADD CONSTRAINT books_pkey PRIMARY KEY (book_id);


--
-- Name: greek_entries greek_entries_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.greek_entries
    ADD CONSTRAINT greek_entries_pkey PRIMARY KEY (entry_id);


--
-- Name: greek_morphology_codes greek_morphology_codes_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.greek_morphology_codes
    ADD CONSTRAINT greek_morphology_codes_pkey PRIMARY KEY (code);


--
-- Name: greek_nt_words greek_nt_words_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.greek_nt_words
    ADD CONSTRAINT greek_nt_words_pkey PRIMARY KEY (word_id);


--
-- Name: hebrew_entries hebrew_entries_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.hebrew_entries
    ADD CONSTRAINT hebrew_entries_pkey PRIMARY KEY (entry_id);


--
-- Name: hebrew_entries hebrew_entries_strongs_id_key; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.hebrew_entries
    ADD CONSTRAINT hebrew_entries_strongs_id_key UNIQUE (strongs_id);


--
-- Name: hebrew_morphology_codes hebrew_morphology_codes_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.hebrew_morphology_codes
    ADD CONSTRAINT hebrew_morphology_codes_pkey PRIMARY KEY (code);


--
-- Name: hebrew_ot_words hebrew_ot_words_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.hebrew_ot_words
    ADD CONSTRAINT hebrew_ot_words_pkey PRIMARY KEY (word_id);


--
-- Name: verses unique_verse; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verses
    ADD CONSTRAINT unique_verse UNIQUE (book_name, chapter_num, verse_num, translation_source);


--
-- Name: hebrew_ot_words unique_verse_word; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.hebrew_ot_words
    ADD CONSTRAINT unique_verse_word UNIQUE (verse_id, word_position);


--
-- Name: verse_embeddings verse_embeddings_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verse_embeddings
    ADD CONSTRAINT verse_embeddings_pkey PRIMARY KEY (id);


--
-- Name: verse_embeddings verse_embeddings_verse_id_translation_source_key; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verse_embeddings
    ADD CONSTRAINT verse_embeddings_verse_id_translation_source_key UNIQUE (verse_id, translation_source);


--
-- Name: verse_word_links verse_word_links_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verse_word_links
    ADD CONSTRAINT verse_word_links_pkey PRIMARY KEY (id);


--
-- Name: verse_word_links verse_word_links_verse_id_word_id_word_type_key; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verse_word_links
    ADD CONSTRAINT verse_word_links_verse_id_word_id_word_type_key UNIQUE (verse_id, word_id, word_type);


--
-- Name: verses verses_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verses
    ADD CONSTRAINT verses_pkey PRIMARY KEY (verse_id);


--
-- Name: versification_mappings versification_mappings_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.versification_mappings
    ADD CONSTRAINT versification_mappings_pkey PRIMARY KEY (mapping_id);


--
-- Name: langchain_pg_collection langchain_pg_collection_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.langchain_pg_collection
    ADD CONSTRAINT langchain_pg_collection_name_key UNIQUE (name);


--
-- Name: langchain_pg_collection langchain_pg_collection_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.langchain_pg_collection
    ADD CONSTRAINT langchain_pg_collection_pkey PRIMARY KEY (uuid);


--
-- Name: langchain_pg_embedding langchain_pg_embedding_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.langchain_pg_embedding
    ADD CONSTRAINT langchain_pg_embedding_pkey PRIMARY KEY (id);


--
-- Name: idx_greek_strongs; Type: INDEX; Schema: bible; Owner: postgres
--

CREATE INDEX idx_greek_strongs ON bible.greek_entries USING btree (strongs_id);


--
-- Name: idx_greek_words_verse; Type: INDEX; Schema: bible; Owner: postgres
--

CREATE INDEX idx_greek_words_verse ON bible.greek_nt_words USING btree (verse_id);


--
-- Name: idx_hebrew_ot_words_strongs; Type: INDEX; Schema: bible; Owner: postgres
--

CREATE INDEX idx_hebrew_ot_words_strongs ON bible.hebrew_ot_words USING btree (strongs_id);


--
-- Name: idx_hebrew_strongs; Type: INDEX; Schema: bible; Owner: postgres
--

CREATE INDEX idx_hebrew_strongs ON bible.hebrew_entries USING btree (strongs_id);


--
-- Name: idx_hebrew_words_verse; Type: INDEX; Schema: bible; Owner: postgres
--

CREATE INDEX idx_hebrew_words_verse ON bible.hebrew_ot_words USING btree (verse_id);


--
-- Name: idx_verse_embeddings_translation; Type: INDEX; Schema: bible; Owner: postgres
--

CREATE INDEX idx_verse_embeddings_translation ON bible.verse_embeddings USING btree (translation_source);


--
-- Name: idx_verse_embeddings_vector; Type: INDEX; Schema: bible; Owner: postgres
--

CREATE INDEX idx_verse_embeddings_vector ON bible.verse_embeddings USING ivfflat (embedding public.vector_cosine_ops) WITH (lists='100');


--
-- Name: idx_verse_embeddings_verse_id; Type: INDEX; Schema: bible; Owner: postgres
--

CREATE INDEX idx_verse_embeddings_verse_id ON bible.verse_embeddings USING btree (verse_id);


--
-- Name: idx_verses_ref; Type: INDEX; Schema: bible; Owner: postgres
--

CREATE INDEX idx_verses_ref ON bible.verses USING btree (book_name, chapter_num, verse_num);


--
-- Name: idx_verses_reference; Type: INDEX; Schema: bible; Owner: postgres
--

CREATE INDEX idx_verses_reference ON bible.verses USING btree (book_name, chapter_num, verse_num);


--
-- Name: verses_embedding_idx; Type: INDEX; Schema: bible; Owner: postgres
--

CREATE INDEX verses_embedding_idx ON bible.verses USING hnsw (embedding public.vector_cosine_ops);


--
-- Name: ix_cmetadata_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cmetadata_gin ON public.langchain_pg_embedding USING gin (cmetadata jsonb_path_ops);


--
-- Name: ix_langchain_pg_embedding_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_langchain_pg_embedding_id ON public.langchain_pg_embedding USING btree (id);


--
-- Name: book_abbreviations book_abbreviations_book_name_fkey; Type: FK CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.book_abbreviations
    ADD CONSTRAINT book_abbreviations_book_name_fkey FOREIGN KEY (book_name) REFERENCES bible.books(name);


--
-- Name: greek_nt_words greek_nt_words_verse_id_fkey; Type: FK CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.greek_nt_words
    ADD CONSTRAINT greek_nt_words_verse_id_fkey FOREIGN KEY (verse_id) REFERENCES bible.verses(verse_id);


--
-- Name: hebrew_ot_words hebrew_ot_words_verse_id_fkey; Type: FK CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.hebrew_ot_words
    ADD CONSTRAINT hebrew_ot_words_verse_id_fkey FOREIGN KEY (verse_id) REFERENCES bible.verses(verse_id);


--
-- Name: verse_word_links verse_word_links_verse_id_fkey; Type: FK CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verse_word_links
    ADD CONSTRAINT verse_word_links_verse_id_fkey FOREIGN KEY (verse_id) REFERENCES bible.verses(verse_id);


--
-- Name: verses verses_book_name_fkey; Type: FK CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verses
    ADD CONSTRAINT verses_book_name_fkey FOREIGN KEY (book_name) REFERENCES bible.books(name);


--
-- Name: langchain_pg_embedding langchain_pg_embedding_collection_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.langchain_pg_embedding
    ADD CONSTRAINT langchain_pg_embedding_collection_id_fkey FOREIGN KEY (collection_id) REFERENCES public.langchain_pg_collection(uuid) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

