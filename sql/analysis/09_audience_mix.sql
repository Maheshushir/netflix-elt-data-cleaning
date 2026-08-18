-- 09 | Audience band mix over time
-- Shows whether the catalogue skews more adult as it grows. The bands come from
-- the rating mapping in staging, which folds the 14 raw codes into 5 groups.
SELECT
    year_added,
    audience_band,
    COUNT(*) AS titles,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY year_added), 1)
        AS pct_of_year,
    ROUND(AVG(duration_minutes), 0) AS avg_movie_minutes
FROM dim_title
WHERE year_added IS NOT NULL AND audience_band IS NOT NULL
GROUP BY year_added, audience_band
ORDER BY year_added, titles DESC;
