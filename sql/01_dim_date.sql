-- sql/01_dim_date.sql
-- Crée une dimension date quotidienne pour 10 ans
CREATE OR REPLACE TABLE `${PROJECT}.${DATASET}.dim_date` AS
WITH dates AS (
  SELECT DATE_ADD('2018-01-01', INTERVAL n DAY) AS dt
  FROM UNNEST(GENERATE_ARRAY(0, 3650)) AS n  -- ~10 ans
)
SELECT
  dt AS date_key,
  EXTRACT(YEAR  FROM dt) AS year,
  EXTRACT(QUARTER FROM dt) AS quarter,
  EXTRACT(MONTH FROM dt) AS month,
  EXTRACT(DAY   FROM dt) AS day,
  FORMAT_DATE('%A', dt) AS weekday_name,
  EXTRACT(ISOWEEK FROM dt) AS iso_week,
  CASE WHEN EXTRACT(DAYOFWEEK FROM dt) IN (1,7) THEN TRUE ELSE FALSE END AS is_weekend
FROM dates;
