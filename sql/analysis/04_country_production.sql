-- 04 | Production by country -- only answerable after the explode
-- co_produced_titles counts titles where this country is one of several, which
-- the raw comma-packed column cannot express at all.
SELECT
    c.country,
    COUNT(*) AS titles,
    SUM(CASE WHEN c.is_primary_country THEN 1 ELSE 0 END)     AS primary_titles,
    SUM(CASE WHEN c.country_count > 1  THEN 1 ELSE 0 END)     AS co_produced_titles,
    SUM(CASE WHEN c.title_type = 'Movie'   THEN 1 ELSE 0 END) AS movies,
    SUM(CASE WHEN c.title_type = 'TV Show' THEN 1 ELSE 0 END) AS tv_shows,
    ROUND(100.0 * SUM(CASE WHEN c.title_type = 'TV Show' THEN 1 ELSE 0 END) / COUNT(*), 1)
        AS pct_tv,
    ROUND(AVG(d.release_year), 0) AS avg_release_year,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_all_credits
FROM int_title_countries c
JOIN dim_title d ON d.show_id = c.show_id
GROUP BY c.country
ORDER BY titles DESC;
