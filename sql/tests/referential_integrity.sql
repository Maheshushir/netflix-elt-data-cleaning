-- TEST | Every bridge-table row must point at a title that exists in dim_title.
-- Wrapped in a CTE for the same reason as not_null_keys: HAVING after UNION ALL
-- would only check the last branch.
WITH orphan_counts AS (
    SELECT 'int_title_countries' AS model, COUNT(*) AS orphans
    FROM int_title_countries b
    LEFT JOIN dim_title d USING (show_id)
    WHERE d.show_id IS NULL
    UNION ALL
    SELECT 'int_title_genres', COUNT(*)
    FROM int_title_genres b
    LEFT JOIN dim_title d USING (show_id)
    WHERE d.show_id IS NULL
    UNION ALL
    SELECT 'int_title_people', COUNT(*)
    FROM int_title_people b
    LEFT JOIN dim_title d USING (show_id)
    WHERE d.show_id IS NULL
)
SELECT model, orphans
FROM orphan_counts
WHERE orphans > 0
