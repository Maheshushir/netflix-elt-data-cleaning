-- 05 | Genre mix, using the normalised labels
-- Netflix tags 'TV Dramas' and 'Dramas' separately. Normalising is what lets a
-- genre be measured across both formats instead of appearing twice at half size.
SELECT
    g.genre_normalised AS genre,
    COUNT(*) AS titles,
    SUM(CASE WHEN g.title_type = 'Movie'   THEN 1 ELSE 0 END) AS movies,
    SUM(CASE WHEN g.title_type = 'TV Show' THEN 1 ELSE 0 END) AS tv_shows,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_genre_tags,
    ROUND(AVG(d.duration_minutes), 1) AS avg_movie_minutes,
    ROUND(AVG(d.seasons), 2)          AS avg_seasons,
    ROUND(AVG(d.release_year), 0)     AS avg_release_year,
    COUNT(DISTINCT d.primary_country) AS countries_producing
FROM int_title_genres g
JOIN dim_title d ON d.show_id = g.show_id
GROUP BY g.genre_normalised
ORDER BY titles DESC;
