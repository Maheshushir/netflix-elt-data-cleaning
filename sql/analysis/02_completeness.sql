-- 02 | Catalogue completeness, by field and by title type
-- Missingness is not uniform across the catalogue, and where it concentrates
-- changes what the gaps actually mean.
SELECT
    title_type,
    COUNT(*) AS titles,
    ROUND(100.0 * SUM(CASE WHEN missing_director   THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_missing_director,
    ROUND(100.0 * SUM(CASE WHEN missing_cast       THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_missing_cast,
    ROUND(100.0 * SUM(CASE WHEN missing_country    THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_missing_country,
    ROUND(100.0 * SUM(CASE WHEN missing_date_added THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_missing_date_added,
    ROUND(100.0 * SUM(CASE WHEN missing_rating     THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_missing_rating,
    ROUND(AVG(completeness_score), 2) AS avg_completeness_score,
    ROUND(100.0 * SUM(CASE WHEN completeness_score = 5 THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS pct_fully_complete
FROM dim_title
GROUP BY title_type
ORDER BY titles DESC;
