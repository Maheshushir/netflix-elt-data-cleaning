-- intermediate | Explode `listed_in` to one row per (title, genre).
--
-- Netflix's own genre labels are type-specific: 'TV Dramas' and 'Dramas' are
-- the same genre applied to different formats, as are 'TV Comedies'/'Comedies'
-- and 'TV Horror'/'Horror Movies'. Left alone, every genre chart splits each
-- category in two and no genre looks as big as it is.
--
-- `genre` keeps Netflix's label verbatim; `genre_normalised` collapses the
-- format prefix so cross-format analysis is possible. Both are exposed rather
-- than one replacing the other -- the raw label is still the right answer for
-- "what does Netflix call this?"

SELECT
    s.show_id,
    s.title_type,
    TRIM(genre_token)                               AS genre,
    genre_index                                     AS genre_position,
    COUNT(*) OVER (PARTITION BY s.show_id)          AS genre_count,

    CASE TRIM(genre_token)
        WHEN 'TV Dramas'            THEN 'Dramas'
        WHEN 'TV Comedies'          THEN 'Comedies'
        WHEN 'TV Action & Adventure' THEN 'Action & Adventure'
        WHEN 'TV Horror'            THEN 'Horror'
        WHEN 'Horror Movies'        THEN 'Horror'
        WHEN 'TV Thrillers'         THEN 'Thrillers'
        WHEN 'TV Mysteries'         THEN 'Mysteries'
        WHEN 'TV Sci-Fi & Fantasy'  THEN 'Sci-Fi & Fantasy'
        WHEN 'Sci-Fi & Fantasy'     THEN 'Sci-Fi & Fantasy'
        WHEN 'Romantic TV Shows'    THEN 'Romance'
        WHEN 'Romantic Movies'      THEN 'Romance'
        WHEN 'International TV Shows' THEN 'International'
        WHEN 'International Movies' THEN 'International'
        WHEN 'Documentaries'        THEN 'Documentary'
        WHEN 'Docuseries'           THEN 'Documentary'
        WHEN 'Kids'' TV'            THEN 'Kids'
        WHEN 'Children & Family Movies' THEN 'Kids'
        WHEN 'Stand-Up Comedy & Talk Shows' THEN 'Stand-Up Comedy'
        WHEN 'Independent Movies'   THEN 'Independent'
        WHEN 'Classic & Cult TV'    THEN 'Classic & Cult'
        WHEN 'Classic Movies'       THEN 'Classic & Cult'
        WHEN 'Cult Movies'          THEN 'Classic & Cult'
        WHEN 'Crime TV Shows'       THEN 'Crime'
        WHEN 'Music & Musicals'     THEN 'Music'
        ELSE TRIM(genre_token)
    END                                             AS genre_normalised
FROM stg_netflix_titles s
CROSS JOIN UNNEST(STRING_SPLIT(s.genres_raw, ','))
    WITH ORDINALITY AS t(genre_token, genre_index)
WHERE s.genres_raw IS NOT NULL
  AND TRIM(genre_token) <> ''
