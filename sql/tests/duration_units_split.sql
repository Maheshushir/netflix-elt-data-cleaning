-- TEST | The mixed-unit `duration` column must resolve to exactly one measure.
-- A movie has minutes and no seasons; a TV show has seasons and no minutes.
-- Any row with both, or neither, means the split logic missed a format.
SELECT show_id, title, title_type, duration_minutes, seasons
FROM dim_title
WHERE (duration_minutes IS NOT NULL AND seasons IS NOT NULL)
   OR (duration_minutes IS NULL     AND seasons IS NULL)
   OR (title_type = 'Movie'   AND duration_minutes IS NULL)
   OR (title_type = 'TV Show' AND seasons IS NULL)
