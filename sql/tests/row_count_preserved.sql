-- TEST | The staging layer must neither invent nor lose rows.
-- Cleaning changes values; it must never change the grain.
SELECT
    (SELECT COUNT(*) FROM raw.netflix_titles) AS raw_rows,
    (SELECT COUNT(*) FROM dim_title)          AS mart_rows
WHERE (SELECT COUNT(*) FROM raw.netflix_titles) <> (SELECT COUNT(*) FROM dim_title)
