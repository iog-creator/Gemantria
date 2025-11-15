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

SET default_tablespace = '';

SET default_table_access_method = heap;

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
-- Name: verses verse_id; Type: DEFAULT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verses ALTER COLUMN verse_id SET DEFAULT nextval('bible.verses_verse_id_seq'::regclass);


--
-- Name: verses unique_verse; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verses
    ADD CONSTRAINT unique_verse UNIQUE (book_name, chapter_num, verse_num, translation_source);


--
-- Name: verses verses_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verses
    ADD CONSTRAINT verses_pkey PRIMARY KEY (verse_id);


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
-- Name: verses verses_book_name_fkey; Type: FK CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.verses
    ADD CONSTRAINT verses_book_name_fkey FOREIGN KEY (book_name) REFERENCES bible.books(name);


--
-- PostgreSQL database dump complete
--

