-- marts | One row per title: the clean, analysis-ready catalogue table.
--
-- Re-attaches the exploded dimensions as counts and primary values, so the
-- common questions ("how many countries?", "what is the main genre?") do not
-- require a join, while the bridge tables remain available for the ones that do.

WITH country_agg AS (
    SELECT
        show_id,
        MAX(CASE WHEN is_primary_country THEN country END) AS primary_country,
        MAX(country_count)                                 AS country_count,
        STRING_AGG(country, ', ' ORDER BY country_position) AS all_countries
    FROM int_title_countries
    GROUP BY show_id
),
genre_agg AS (
    SELECT
        show_id,
        MAX(CASE WHEN genre_position = 1 THEN genre_normalised END) AS primary_genre,
        MAX(genre_count)                                            AS genre_count,
        STRING_AGG(genre_normalised, ', ' ORDER BY genre_position)  AS all_genres
    FROM int_title_genres
    GROUP BY show_id
),
people_agg AS (
    SELECT
        show_id,
        COUNT(*) FILTER (WHERE role = 'actor')    AS cast_size,
        COUNT(*) FILTER (WHERE role = 'director') AS director_count,
        STRING_AGG(person_name, ', ') FILTER (WHERE role = 'director')
                                                  AS directors
    FROM int_title_people
    GROUP BY show_id
)
SELECT
    s.show_id,
    s.title,
    s.title_type,
    s.release_year,
    s.date_added,
    s.year_added,
    s.month_added,
    s.years_release_to_platform,
    s.rating,
    s.audience_band,
    s.duration_minutes,
    s.seasons,

    c.primary_country,
    c.country_count,
    c.all_countries,
    g.primary_genre,
    g.genre_count,
    g.all_genres,
    p.cast_size,
    p.director_count,
    p.directors,

    s.description,

    -- Completeness flags: which fields were missing in the source. Retaining
    -- this makes "how complete is the catalogue?" a query rather than a
    -- forensic exercise against the raw table.
    s.director_raw IS NULL  AS missing_director,
    s.cast_raw     IS NULL  AS missing_cast,
    s.country_raw  IS NULL  AS missing_country,
    s.date_added   IS NULL  AS missing_date_added,
    s.rating       IS NULL  AS missing_rating,

    -- A single 0-5 score for how complete each row is.
    (CASE WHEN s.director_raw IS NOT NULL THEN 1 ELSE 0 END
   + CASE WHEN s.cast_raw     IS NOT NULL THEN 1 ELSE 0 END
   + CASE WHEN s.country_raw  IS NOT NULL THEN 1 ELSE 0 END
   + CASE WHEN s.date_added   IS NOT NULL THEN 1 ELSE 0 END
   + CASE WHEN s.rating       IS NOT NULL THEN 1 ELSE 0 END) AS completeness_score

FROM stg_netflix_titles s
LEFT JOIN country_agg c ON c.show_id = s.show_id
LEFT JOIN genre_agg   g ON g.show_id = s.show_id
LEFT JOIN people_agg  p ON p.show_id = s.show_id
