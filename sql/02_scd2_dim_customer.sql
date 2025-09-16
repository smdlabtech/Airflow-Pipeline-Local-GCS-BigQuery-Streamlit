-- sql/02_scd2_dim_customer.sql
-- Exemple SCD2 : maintient une dim_customer_history à partir de clean_customers
CREATE TABLE IF NOT EXISTS `${PROJECT}.${DATASET}.dim_customer_history` (
  customer_id INT64,
  first_name STRING,
  last_name STRING,
  email STRING,
  country STRING,
  effective_from TIMESTAMP,
  effective_to   TIMESTAMP,
  is_current     BOOL
);

MERGE `${PROJECT}.${DATASET}.dim_customer_history` T
USING (
  SELECT customer_id, first_name, last_name, email, country FROM `${PROJECT}.${DATASET}.clean_customers`
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
