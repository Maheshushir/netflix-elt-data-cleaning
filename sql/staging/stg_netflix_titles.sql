-- staging | One row per title, typed and trimmed. Still one row per source row.
--
-- Every cleaning decision in this file is a decision about *meaning*, not
-- formatting, and each is commented with what the source actually contains.
-- Materialised as a VIEW: it is cheap, and keeping it a view means the raw
-- table stays the single source of truth.

SELECT
    TRIM(show_id)                                       AS show_id,
    TRIM(type)                                          AS title_type,
    TRIM(title)                                         AS title,

    -- 2,389 of 7,787 rows (30.7%) have no director. NULL is preserved rather
    -- than filled with 'Unknown': a missing director is a fact about the
    -- catalogue, and COUNT()/AVG() must not treat it as a real value. The
    -- presentation layer decides how to display it.
    NULLIF(TRIM(director), '')                          AS director_raw,
    NULLIF(TRIM("cast"), '')                            AS cast_raw,
    NULLIF(TRIM(country), '')                           AS country_raw,
    NULLIF(TRIM(listed_in), '')                         AS genres_raw,

    -- 88 date_added values carry a leading space (' March 15, 2019').
    --
    -- DuckDB's strptime happens to tolerate that; pandas' to_datetime with the
    -- same format string does not, and returns NaT. So the identical cleaning
    -- logic gives different answers depending on which engine runs it -- 88
    -- rows silently vanish from the "titles added per month" series in one and
    -- not the other. The TRIM is not redundant defensive coding; it is what
    -- makes the result engine-independent. `sql/tests/date_added_parsed.sql`
    -- pins the behaviour so a future refactor cannot quietly drop it.
    TRY_STRPTIME(TRIM(date_added), '%B %d, %Y')         AS date_added,

    TRY_CAST(TRIM(release_year) AS INTEGER)             AS release_year,
    NULLIF(TRIM(rating), '')                            AS rating,

    -- `duration` mixes two different units in one column: '93 min' for films
    -- and '4 Seasons' for series. Splitting it is not cosmetic -- leaving it as
    -- text makes the column unusable for arithmetic, and casting it naively
    -- would silently compare 93 minutes against 4 seasons on the same axis.
    CASE
        WHEN duration ILIKE '%min%'
        THEN TRY_CAST(REGEXP_EXTRACT(duration, '(\d+)', 1) AS INTEGER)
    END                                                 AS duration_minutes,
    CASE
        WHEN duration ILIKE '%season%'
        THEN TRY_CAST(REGEXP_EXTRACT(duration, '(\d+)', 1) AS INTEGER)
    END                                                 AS seasons,
    NULLIF(TRIM(duration), '')                          AS duration_raw,

    NULLIF(TRIM(description), '')                       AS description,

    -- Derived attributes used across the marts.
    EXTRACT(YEAR  FROM TRY_STRPTIME(TRIM(date_added), '%B %d, %Y')) AS year_added,
    EXTRACT(MONTH FROM TRY_STRPTIME(TRIM(date_added), '%B %d, %Y')) AS month_added,

    -- The gap between a title's release and its arrival on the platform tells
    -- you whether Netflix is buying back-catalogue or commissioning new work.
    EXTRACT(YEAR FROM TRY_STRPTIME(TRIM(date_added), '%B %d, %Y'))
        - TRY_CAST(TRIM(release_year) AS INTEGER)       AS years_release_to_platform,

    -- Ratings collapse to four audience bands. TV-Y7-FV ("fantasy violence")
    -- and UR/NR ("unrated"/"not rated") are the awkward ones; UR and NR mean
    -- the same thing and are folded together.
    CASE
        WHEN TRIM(rating) IN ('G', 'TV-G', 'TV-Y')                 THEN 'Kids'
        WHEN TRIM(rating) IN ('PG', 'TV-PG', 'TV-Y7', 'TV-Y7-FV')  THEN 'Older kids'
        WHEN TRIM(rating) IN ('PG-13', 'TV-14')                    THEN 'Teens'
        WHEN TRIM(rating) IN ('R', 'NC-17', 'TV-MA')               THEN 'Adults'
        WHEN TRIM(rating) IN ('NR', 'UR')                          THEN 'Unrated'
        ELSE NULL
    END                                                 AS audience_band

FROM raw.netflix_titles
WHERE show_id IS NOT NULL
