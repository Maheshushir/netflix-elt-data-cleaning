-- TEST | show_id must be unique. Returns offending rows; 0 rows = pass.
SELECT show_id, COUNT(*) AS n
FROM dim_title
GROUP BY show_id
HAVING COUNT(*) > 1
