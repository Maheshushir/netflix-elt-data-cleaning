-- 07 | The people Netflix works with most
-- Requires the people bridge: the source packs up to 50 names into one cell,
-- so no amount of GROUP BY on the raw column answers this.
SELECT
    p.person_name,
    p.role,
    COUNT(*) AS credits,
    SUM(CASE WHEN p.title_type = 'Movie'   THEN 1 ELSE 0 END) AS movies,
    SUM(CASE WHEN p.title_type = 'TV Show' THEN 1 ELSE 0 END) AS tv_shows,
    SUM(CASE WHEN p.is_top_billed THEN 1 ELSE 0 END)          AS top_billed_credits,
    COUNT(DISTINCT d.primary_country) AS countries,
    MIN(d.release_year) AS first_year,
    MAX(d.release_year) AS last_year
FROM int_title_people p
JOIN dim_title d ON d.show_id = p.show_id
GROUP BY p.person_name, p.role
HAVING COUNT(*) >= 10
ORDER BY credits DESC;
