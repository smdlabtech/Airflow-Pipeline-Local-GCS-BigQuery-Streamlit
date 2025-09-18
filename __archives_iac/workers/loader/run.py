import os, argparse, sys
from utils import gcp_bq, gcp_io

PROJECT = os.getenv("PROJECT_ID", "bq-small-corp")
DATASET = os.getenv("BQ_DATASET", "demo_dw")
LOCATION = os.getenv("BQ_LOCATION", "EU")
BUCKET = os.getenv("GCS_BUCKET", "bq-small-corp-data")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--uris", nargs="+", help="GCS URIs to load", required=False)
    parser.add_argument("--table", help="staging table name", default="staging_customers")
    parser.add_argument("--export_table", help="table to export to GCS", default=None)
    parser.add_argument("--export_uri", help="dest GCS (gs://.../*.parquet)", default=None)
    args = parser.parse_args()

    print(f"[cfg] project={PROJECT} dataset={DATASET} location={LOCATION} bucket={BUCKET}")
    gcp_bq.ensure_dataset(PROJECT, DATASET, LOCATION)

    if args.uris:
        print(f"[load] {args.uris} -> {PROJECT}.{DATASET}.{args.table}")
        gcp_bq.load_gcs_to_bq(PROJECT, DATASET, args.table, args.uris, autodetect=True, write_disposition="WRITE_TRUNCATE")

    # minimal clean + dim/fact
    sql_clean = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.clean_customers` AS
SELECT DISTINCT
  CAST(customer_id AS INT64) AS customer_id,
  TRIM(first_name) AS first_name,
  TRIM(last_name)  AS last_name,
  LOWER(email)     AS email,
  country
FROM `{PROJECT}.{DATASET}.staging_customers`
WHERE customer_id IS NOT NULL;
"""
    gcp_bq.run_query(sql_clean, project=PROJECT)
    print("[sql] clean_customers done.")

    sql_dim_date = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.dim_date` AS
WITH dates AS (
  SELECT DATE_ADD('2018-01-01', INTERVAL n DAY) AS dt
  FROM UNNEST(GENERATE_ARRAY(0, 3650)) AS n
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
"""
    gcp_bq.run_query(sql_dim_date, project=PROJECT)
    print("[sql] dim_date done.")

    sql_dim = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.dim_customer` AS
SELECT customer_id, first_name, last_name, email, country
FROM `{PROJECT}.{DATASET}.clean_customers`;
"""
    gcp_bq.run_query(sql_dim, project=PROJECT)
    print("[sql] dim_customer done.")

    sql_fact = f"""
CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.fact_orders` AS
SELECT
  CAST(order_id AS INT64) AS order_id,
  CAST(customer_id AS INT64) AS customer_id,
  DATE(order_date) AS order_date,
  CAST(order_amount AS NUMERIC) AS order_amount
FROM `{PROJECT}.{DATASET}.staging_orders`;
"""
    gcp_bq.run_query(sql_fact, project=PROJECT)
    print("[sql] fact_orders done.")

    sql_scd2 = f"""
CREATE TABLE IF NOT EXISTS `{PROJECT}.{DATASET}.dim_customer_history` (
  customer_id INT64,
  first_name STRING,
  last_name STRING,
  email STRING,
  country STRING,
  effective_from TIMESTAMP,
  effective_to   TIMESTAMP,
  is_current     BOOL
);
MERGE `{PROJECT}.{DATASET}.dim_customer_history` T
USING (
  SELECT customer_id, first_name, last_name, email, country
  FROM `{PROJECT}.{DATASET}.clean_customers`
) S
ON T.customer_id = S.customer_id AND T.is_current = TRUE
WHEN MATCHED AND (
     T.first_name != S.first_name OR
     T.last_name  != S.last_name  OR
     T.email      != S.email      OR
     T.country    != S.country
) THEN
  UPDATE SET effective_to = CURRENT_TIMESTAMP(), is_current = FALSE
WHEN NOT MATCHED BY TARGET THEN
  INSERT (customer_id, first_name, last_name, email, country, effective_from, effective_to, is_current)
  VALUES (S.customer_id, S.first_name, S.last_name, S.email, S.country, CURRENT_TIMESTAMP(), NULL, TRUE);
"""
    gcp_bq.run_query(sql_scd2, project=PROJECT)
    print("[sql] SCD2 done.")

    if args.export_table and args.export_uri:
        print(f"[export] {args.export_table} -> {args.export_uri}")
        job = gcp_bq.extract_table_to_gcs(table=args.export_table, destination_uri=args.export_uri, fmt="PARQUET")
        print(f"[export] job={job.job_id} done")

if __name__ == "__main__":
    sys.exit(main())
