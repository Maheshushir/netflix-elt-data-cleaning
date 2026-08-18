-- intermediate | Explode `cast` and `director` into one row per (title, person).
--
-- The two columns are unioned into a single people bridge with a `role`
-- discriminator rather than kept as two tables: the same human appears in both
-- (directors who act, actors who direct), and a single table is what makes
-- "who does Netflix work with most?" answerable in one GROUP BY.
--
-- `cast` is a reserved word in most SQL dialects, which is exactly the kind of
-- thing that breaks a pipeline three layers downstream. Staging renamed it to
-- cast_raw so nothing below ever has to quote it.

WITH actors AS (
    SELECT
        s.show_id,
        s.title_type,
        TRIM(person_token)  AS person_name,
        'actor'             AS role,
        person_index        AS billing_position
    FROM stg_netflix_titles s
    CROSS JOIN UNNEST(STRING_SPLIT(s.cast_raw, ','))
        WITH ORDINALITY AS t(person_token, person_index)
    WHERE s.cast_raw IS NOT NULL
      AND TRIM(person_token) <> ''
),
directors AS (
    SELECT
        s.show_id,
        s.title_type,
        TRIM(person_token)  AS person_name,
        'director'          AS role,
        person_index        AS billing_position
    FROM stg_netflix_titles s
    CROSS JOIN UNNEST(STRING_SPLIT(s.director_raw, ','))
        WITH ORDINALITY AS t(person_token, person_index)
    WHERE s.director_raw IS NOT NULL
      AND TRIM(person_token) <> ''
)
SELECT
    show_id,
    title_type,
    person_name,
    role,
    billing_position,
    -- Top billing is a meaningful signal: a lead role is not a cameo.
    role = 'actor' AND billing_position <= 3 AS is_top_billed
FROM actors
UNION ALL
SELECT
    show_id, title_type, person_name, role, billing_position, FALSE
FROM directors
