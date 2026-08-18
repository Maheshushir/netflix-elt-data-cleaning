-- intermediate | Explode the comma-separated `country` field to one row per
-- (title, country).
--
-- The source packs up to 12 countries into a single cell. Any analysis that
-- groups by the raw column treats 'United States, India' as a country in its
-- own right -- which is how portfolio projects end up reporting 118 "countries"
-- for a dataset that covers about 90.
--
-- Two traps handled here:
--   1. Trailing commas ('United States, ') produce an empty token after the
--      split. Filtering them out is why the distinct count comes down.
--   2. Tokens carry leading spaces after the split, so ' India' and 'India'
--      would be counted as two different countries without the TRIM.

SELECT
    s.show_id,
    s.title_type,
    TRIM(country_token)                             AS country,
    -- Position matters: the first-listed country is conventionally the primary
    -- production country, and co-productions are ordered by contribution.
    country_index                                   AS country_position,
    country_index = 1                               AS is_primary_country,
    -- How many countries co-produced this title at all.
    COUNT(*) OVER (PARTITION BY s.show_id)          AS country_count
FROM stg_netflix_titles s
CROSS JOIN UNNEST(STRING_SPLIT(s.country_raw, ','))
    WITH ORDINALITY AS t(country_token, country_index)
WHERE s.country_raw IS NOT NULL
  AND TRIM(country_token) <> ''
