-- 01 | What the cleaning actually changed
-- The headline table of this project: a naive COUNT(DISTINCT) against the raw
-- column, versus the same count against the exploded and normalised models.
WITH raw_counts AS (
    SELECT
        COUNT(DISTINCT TRIM(country))   AS raw_country_strings,
        COUNT(DISTINCT TRIM(listed_in)) AS raw_genre_strings
    FROM raw.netflix_titles
),
clean_counts AS (
    SELECT
        (SELECT COUNT(DISTINCT country)          FROM int_title_countries) AS real_countries,
        (SELECT COUNT(DISTINCT genre)            FROM int_title_genres)    AS netflix_genre_labels,
        (SELECT COUNT(DISTINCT genre_normalised) FROM int_title_genres)    AS normalised_genres
)
SELECT 'country' AS field,
       raw_country_strings AS naive_distinct_count,
       real_countries      AS true_distinct_count,
       raw_country_strings - real_countries AS overcount
FROM raw_counts, clean_counts
UNION ALL
SELECT 'genre (Netflix labels)', raw_genre_strings, netflix_genre_labels,
       raw_genre_strings - netflix_genre_labels
FROM raw_counts, clean_counts
UNION ALL
SELECT 'genre (normalised)', raw_genre_strings, normalised_genres,
       raw_genre_strings - normalised_genres
FROM raw_counts, clean_counts;
