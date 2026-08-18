-- TEST | title_type is a closed set of two values.
SELECT DISTINCT title_type
FROM dim_title
WHERE title_type NOT IN ('Movie', 'TV Show')
