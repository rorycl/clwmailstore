/* 
CLW Mailstore database schema. The oversize email table is optional.
*/

--
-- Name: log; Type: TABLE; Schema: public; Owner: mailusers; Tablespace: 
--

CREATE TABLE log (
    n_id SERIAL NOT NULL,
    dt_created timestamp without time zone DEFAULT now(),
    t_message_date character varying,
    t_message_id character varying,
    t_orig_id character varying,
    t_recipients character varying,
    t_subject character varying,
    n_size integer,
    t_from character varying,
    t_to character varying,
    t_cc character varying,
    t_sha1sum character varying,
    dt_processed timestamp without time zone,
    b_processed boolean DEFAULT false,
    t_path character varying(200)
);

--
-- Name: oversizemail; Type: TABLE; Schema: public; Owner: mailusers; Tablespace: 
--

CREATE TABLE oversizemail (
    n_id SERIAL NOT NULL,
    dt_date timestamp without time zone DEFAULT now(),
    t_message_id character varying(200),
    t_date character varying(200),
    t_to text,
    t_from text,
    t_cc text,
    t_subject text,
    n_size integer,
    b_mailsent boolean DEFAULT false
);

