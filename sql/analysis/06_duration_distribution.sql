-- 06 | Runtime and season-count distributions
-- Only possible because staging split the mixed-unit `duration` column into two
-- properly typed measures. Before that split, this query cannot be written.
SELECT 'Movie' AS title_type, 'minutes' AS unit,
    COUNT(*) AS titles,
    ROUND(MIN(duration_minutes), 0)                 AS min_value,
    ROUND(QUANTILE_CONT(duration_minutes, 0.25), 0) AS p25,
    ROUND(MEDIAN(duration_minutes), 0)              AS median_value,
    ROUND(QUANTILE_CONT(duration_minutes, 0.75), 0) AS p75,
    ROUND(QUANTILE_CONT(duration_minutes, 0.95), 0) AS p95,
    ROUND(MAX(duration_minutes), 0)                 AS max_value,
    ROUND(AVG(duration_minutes), 1)                 AS mean_value
FROM dim_title WHERE duration_minutes IS NOT NULL
UNION ALL
SELECT 'TV Show', 'seasons',
    COUNT(*),
    ROUND(MIN(seasons), 0),
    ROUND(QUANTILE_CONT(seasons, 0.25), 0),
    ROUND(MEDIAN(seasons), 0),
    ROUND(QUANTILE_CONT(seasons, 0.75), 0),
    ROUND(QUANTILE_CONT(seasons, 0.95), 0),
    ROUND(MAX(seasons), 0),
    ROUND(AVG(seasons), 2)
FROM dim_title WHERE seasons IS NOT NULL;
