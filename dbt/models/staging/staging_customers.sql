-- dbt/models/staging/staging_customers.sql
SELECT * FROM {{ source('demo_dw','staging_customers') }}
