-- TEST | The columns every downstream model joins or groups on must be present.
-- The UNION is wrapped in a CTE: a HAVING placed after UNION ALL binds only to
-- the final branch, so it would silently check one column instead of four.
WITH null_counts AS (
    SELECT 'show_id'      AS column_name, COUNT(*) AS null_rows
    FROM dim_title WHERE show_id IS NULL
    UNION ALL
    SELECT 'title',        COUNT(*) FROM dim_title WHERE title        IS NULL
    UNION ALL
    SELECT 'title_type',   COUNT(*) FROM dim_title WHERE title_type   IS NULL
    UNION ALL
    SELECT 'release_year', COUNT(*) FROM dim_title WHERE release_year IS NULL
)
SELECT column_name, null_rows
FROM null_counts
WHERE null_rows > 0
