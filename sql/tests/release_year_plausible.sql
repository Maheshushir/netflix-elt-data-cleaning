-- TEST | Release years must be inside the plausible range for filmed media.
SELECT show_id, title, release_year
FROM dim_title
WHERE release_year < 1900 OR release_year > EXTRACT(YEAR FROM CURRENT_DATE) + 1
