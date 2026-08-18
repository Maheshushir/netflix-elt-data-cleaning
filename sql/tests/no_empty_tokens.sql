-- TEST | Exploding on ',' must not leave empty or untrimmed tokens.
-- Trailing commas in the source ('United States, ') are the cause; this test
-- is what proves the filter in the intermediate models actually works.
SELECT 'country' AS field, country AS value FROM int_title_countries
WHERE country = '' OR country <> TRIM(country)
UNION ALL
SELECT 'genre', genre FROM int_title_genres
WHERE genre = '' OR genre <> TRIM(genre)
UNION ALL
SELECT 'person', person_name FROM int_title_people
WHERE person_name = '' OR person_name <> TRIM(person_name)
