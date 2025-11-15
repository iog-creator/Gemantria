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
-- Name: versification_mappings mapping_id; Type: DEFAULT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.versification_mappings ALTER COLUMN mapping_id SET DEFAULT nextval('bible.versification_mappings_mapping_id_seq'::regclass);


--
-- Name: versification_mappings versification_mappings_pkey; Type: CONSTRAINT; Schema: bible; Owner: postgres
--

ALTER TABLE ONLY bible.versification_mappings
    ADD CONSTRAINT versification_mappings_pkey PRIMARY KEY (mapping_id);


--
-- PostgreSQL database dump complete
--

