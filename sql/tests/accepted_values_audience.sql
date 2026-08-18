-- TEST | Every non-null rating must map to an audience band.
-- Catches a new rating code appearing in a refreshed extract.
SELECT DISTINCT rating
FROM dim_title
WHERE rating IS NOT NULL AND audience_band IS NULL
