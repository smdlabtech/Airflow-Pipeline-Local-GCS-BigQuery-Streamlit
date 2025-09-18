from typing import List, Optional
from google.cloud import bigquery
import pandas as pd

def get_bq_client(project: Optional[str]=None):
    return bigquery.Client(project=project) if project else bigquery.Client()

def ensure_dataset(project_id: str, dataset: str, location: str="EU"):
    client = get_bq_client(project_id)
    ds = bigquery.Dataset(f"{project_id}.{dataset}")
    ds.location = location
    client.create_dataset(ds, exists_ok=True)

def load_gcs_to_bq(project_id: str, dataset: str, table: str, uris: List[str], autodetect: bool=True, write_disposition: str="WRITE_TRUNCATE"):
    client = get_bq_client(project_id)
    table_id = f"{project_id}.{dataset}.{table}"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        autodetect=autodetect,
        write_disposition=write_disposition,
        skip_leading_rows=1,
    )
    load_job = client.load_table_from_uri(uris, table_id, job_config=job_config)
    load_job.result()
    return load_job

def run_query(sql: str, project: Optional[str]=None):
    client = get_bq_client(project)
    job = client.query(sql)
    try:
        return job.result().to_dataframe()
    except Exception:
        return None

def run_query_to_df(sql: str, project: Optional[str]=None) -> pd.DataFrame:
    client = get_bq_client(project)
    return client.query(sql).result().to_dataframe()

def extract_table_to_gcs(table: str, destination_uri: str, fmt: str="PARQUET"):
    client = get_bq_client()
    job_config = bigquery.job.ExtractJobConfig()
    if fmt.upper()=="CSV":
        job_config.destination_format = bigquery.DestinationFormat.CSV
    else:
        job_config.destination_format = bigquery.DestinationFormat.PARQUET
    extract_job = client.extract_table(table, destination_uri, job_config=job_config)
    extract_job.result()
    return extract_job
