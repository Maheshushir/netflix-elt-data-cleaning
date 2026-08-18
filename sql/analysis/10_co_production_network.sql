-- 10 | Co-production: which countries make things together
-- A self-join on the countries bridge. Impossible against the raw column, which
-- stores 'United States, United Kingdom' as one opaque string.
SELECT
    a.country AS country_a,
    b.country AS country_b,
    COUNT(*)  AS co_productions,
    SUM(CASE WHEN d.title_type = 'Movie'   THEN 1 ELSE 0 END) AS movies,
    SUM(CASE WHEN d.title_type = 'TV Show' THEN 1 ELSE 0 END) AS tv_shows,
    ROUND(AVG(d.release_year), 0) AS avg_release_year
FROM int_title_countries a
JOIN int_title_countries b
  ON a.show_id = b.show_id
 AND a.country < b.country              -- each unordered pair counted once
JOIN dim_title d ON d.show_id = a.show_id
GROUP BY a.country, b.country
HAVING COUNT(*) >= 5
ORDER BY co_productions DESC;
