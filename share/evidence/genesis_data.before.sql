--
-- PostgreSQL database dump
--

\restrict Htjmls5iwSbm5FyGWgNDKYk32BasfBHOjSTB9JygHHbIrSF1ObzsN1DH23pQmq7

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
-- Data for Name: concept_network; Type: TABLE DATA; Schema: gematria; Owner: mccoy
--

COPY gematria.concept_network (id, concept_id, embedding, created_at) FROM stdin;
\.


--
-- Data for Name: concept_relations; Type: TABLE DATA; Schema: gematria; Owner: mccoy
--

COPY gematria.concept_relations (relation_id, src_concept_id, dst_concept_id, relation_type, weight, evidence, created_at) FROM stdin;
\.


--
-- Name: concept_network_id_seq; Type: SEQUENCE SET; Schema: gematria; Owner: mccoy
--

SELECT pg_catalog.setval('gematria.concept_network_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

\unrestrict Htjmls5iwSbm5FyGWgNDKYk32BasfBHOjSTB9JygHHbIrSF1ObzsN1DH23pQmq7

