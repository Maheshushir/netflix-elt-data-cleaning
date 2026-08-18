-- 03 | Titles added to the platform per year, split by type
-- Uses date_added (when Netflix acquired the title), not release_year (when it
-- was made). Conflating those two is the most common error with this dataset.
SELECT
    year_added,
    COUNT(*) AS titles_added,
    SUM(CASE WHEN title_type = 'Movie'   THEN 1 ELSE 0 END) AS movies_added,
    SUM(CASE WHEN title_type = 'TV Show' THEN 1 ELSE 0 END) AS shows_added,
    ROUND(100.0 * SUM(CASE WHEN title_type = 'TV Show' THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS pct_tv,
    ROUND(AVG(years_release_to_platform), 1)    AS avg_years_since_release,
    ROUND(MEDIAN(years_release_to_platform), 1) AS median_years_since_release,
    SUM(COUNT(*)) OVER (ORDER BY year_added)    AS cumulative_titles
FROM dim_title
WHERE year_added IS NOT NULL
GROUP BY year_added
ORDER BY year_added;
