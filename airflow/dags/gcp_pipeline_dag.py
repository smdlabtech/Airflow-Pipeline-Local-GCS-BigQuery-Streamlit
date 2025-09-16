# Defaults: PROJECT_ID=bq-small-corp, REGION=europe-west1, BQ LOCATION=EU
# airflow/dags/gcp_pipeline_dag.py
from datetime import datetime
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator

PROJECT_ID = "{{ var.value.project_id }}"
DATASET = "{{ var.value.dataset }}"
BUCKET = "{{ var.value.bucket }}"
LOCATION = "{{ var.value.location or 'EU' }}"

with DAG(
    dag_id="gcp_local_to_bq_pipeline_v2",
    start_date=datetime(2025,1,1),
    schedule_interval=None,
    catchup=False,
    default_args={"owner":"you"},
    tags=["gcp","bq","gcs","scd2","dimdate"]
) as dag:

    load_customers = GCSToBigQueryOperator(
        task_id="load_customers",
        bucket=BUCKET,
        source_objects=["landing/customers*.csv"],
        destination_project_dataset_table=f"{PROJECT_ID}.{DATASET}.staging_customers",
        autodetect=True,
        source_format="CSV",
        write_disposition="WRITE_TRUNCATE",
        skip_leading_rows=1,
        location=LOCATION,
    )

    load_orders = GCSToBigQueryOperator(
        task_id="load_orders",
        bucket=BUCKET,
        source_objects=["landing/orders*.csv"],
        destination_project_dataset_table=f"{PROJECT_ID}.{DATASET}.staging_orders",
        autodetect=True,
        source_format="CSV",
        write_disposition="WRITE_TRUNCATE",
        skip_leading_rows=1,
        location=LOCATION,
    )

    sql_clean = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET}.clean_customers` AS
    SELECT DISTINCT
      CAST(customer_id AS INT64) AS customer_id,
      TRIM(first_name) AS first_name,
      TRIM(last_name)  AS last_name,
      LOWER(email)     AS email,
      country
    FROM `{PROJECT_ID}.{DATASET}.staging_customers`
    WHERE customer_id IS NOT NULL;
    """
    clean_customers = BigQueryInsertJobOperator(
        task_id="clean_customers",
        configuration={"query":{"query":sql_clean,"useLegacySql":False}},
        location=LOCATION,
    )

    sql_dim_date = open("/opt/airflow/dags/sql/01_dim_date.sql").read() if False else f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET}.dim_date` AS
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
    build_dim_date = BigQueryInsertJobOperator(
        task_id="build_dim_date",
        configuration={"query":{"query":sql_dim_date,"useLegacySql":False}},
        location=LOCATION,
    )

    sql_dim = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET}.dim_customer` AS
    SELECT customer_id, first_name, last_name, email, country
    FROM `{PROJECT_ID}.{DATASET}.clean_customers`;
    """
    build_dim_customer = BigQueryInsertJobOperator(
        task_id="build_dim_customer",
        configuration={"query":{"query":sql_dim,"useLegacySql":False}},
        location=LOCATION,
    )

    sql_fact = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET}.fact_orders` AS
    SELECT
      CAST(order_id AS INT64) AS order_id,
      CAST(customer_id AS INT64) AS customer_id,
      DATE(order_date) AS order_date,
      CAST(order_amount AS NUMERIC) AS order_amount
    FROM `{PROJECT_ID}.{DATASET}.staging_orders`;
    """
    build_fact_orders = BigQueryInsertJobOperator(
        task_id="build_fact_orders",
        configuration={"query":{"query":sql_fact,"useLegacySql":False}},
        location=LOCATION,
    )

    sql_scd2 = f"""
    CREATE TABLE IF NOT EXISTS `{PROJECT_ID}.{DATASET}.dim_customer_history` (
      customer_id INT64,
      first_name STRING,
      last_name STRING,
      email STRING,
      country STRING,
      effective_from TIMESTAMP,
      effective_to   TIMESTAMP,
      is_current     BOOL
    );

    MERGE `{PROJECT_ID}.{DATASET}.dim_customer_history` T
    USING (
      SELECT customer_id, first_name, last_name, email, country FROM `{PROJECT_ID}.{DATASET}.clean_customers`
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
    apply_scd2 = BigQueryInsertJobOperator(
        task_id="apply_scd2",
        configuration={"query":{"query":sql_scd2,"useLegacySql":False}},
        location=LOCATION,
    )

    [load_customers, load_orders] >> clean_customers >> build_dim_date >> build_dim_customer >> build_fact_orders >> apply_scd2
