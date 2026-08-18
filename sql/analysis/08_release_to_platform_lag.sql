-- 08 | How long after release does a title reach Netflix?
-- Separates commissioning (same-year arrivals) from back-catalogue licensing.
-- Values <= 0 are legitimate: Originals land the year they are released.
SELECT
    year_added,
    COUNT(*) AS titles,
    ROUND(AVG(years_release_to_platform), 2)    AS avg_lag_years,
    ROUND(MEDIAN(years_release_to_platform), 1) AS median_lag_years,
    SUM(CASE WHEN years_release_to_platform <= 0 THEN 1 ELSE 0 END)
        AS same_year_or_earlier,
    ROUND(100.0 * SUM(CASE WHEN years_release_to_platform <= 0 THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS pct_same_year,
    SUM(CASE WHEN years_release_to_platform > 10 THEN 1 ELSE 0 END)
        AS back_catalogue_over_10y,
    ROUND(100.0 * SUM(CASE WHEN years_release_to_platform > 10 THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS pct_back_catalogue
FROM dim_title
WHERE year_added IS NOT NULL AND years_release_to_platform IS NOT NULL
GROUP BY year_added
ORDER BY year_added;
