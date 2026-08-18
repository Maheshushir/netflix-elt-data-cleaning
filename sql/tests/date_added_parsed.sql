-- TEST | date_added must parse for every row that had a non-empty source value.
-- 88 source values carry a leading space. DuckDB tolerates them, pandas does
-- not, so this test pins the contract at the value level rather than trusting
-- any one engine's leniency: whatever runs the model, an unparsed date that
-- had a source value is a failure.
SELECT r.show_id, r.date_added AS raw_value
FROM raw.netflix_titles r
JOIN dim_title d ON d.show_id = TRIM(r.show_id)
WHERE TRIM(COALESCE(r.date_added, '')) <> ''
  AND d.date_added IS NULL
