import os
import logging
import sys
from google.cloud import storage
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# === Config ===
from config.kafka_config import *

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === BigQuery Configuration ===
PROJECT_ID = storage.Client().project  # Dynamically get the project ID
DATASET_ID = 'stock_data_analytics'
TABLE_ID = 'stock_stream_table'

# === Step 1: Set Google Cloud credentials ===
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS
logger.info(f"Set Google Cloud credentials to {GOOGLE_APPLICATION_CREDENTIALS}")

# === Step 2: Initialize GCS and BigQuery clients ===
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)
bq_client = bigquery.Client(project=PROJECT_ID)

# === Step 3: Create BigQuery dataset and table if they don't exist ===
# Create dataset
dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
try:
    bq_client.get_dataset(dataset_ref)
    logger.info(f"Dataset {DATASET_ID} already exists.")
except NotFound:
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = 'US'  # Adjust based on your region
    bq_client.create_dataset(dataset)
    logger.info(f"Created dataset {DATASET_ID}.")

# Create table
table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
try:
    bq_client.get_table(table_ref)
    logger.info(f"Table {TABLE_ID} already exists.")
except NotFound:
    schema = [
        bigquery.SchemaField("Index", "STRING"),
        bigquery.SchemaField("Date", "STRING"),
        bigquery.SchemaField("Open", "FLOAT"),
        bigquery.SchemaField("High", "FLOAT"),
        bigquery.SchemaField("Low", "FLOAT"),
        bigquery.SchemaField("Close", "FLOAT"),
        bigquery.SchemaField("Adj Close", "FLOAT"),
        bigquery.SchemaField("Volume", "FLOAT"),
        bigquery.SchemaField("CloseUSD", "FLOAT"),
    ]
    table = bigquery.Table(table_ref, schema=schema)
    bq_client.create_table(table)
    logger.info(f"Created table {TABLE_ID}.")

# === Step 4: List NDJSON files in GCS ===
prefix = 'stock-data-'  # NDJSON files start with this prefix
blobs = bucket.list_blobs(prefix=prefix)
ndjson_files = [f"gs://{BUCKET_NAME}/{blob.name}" for blob in blobs if blob.name.endswith('.ndjson')]
logger.info(f"Found {len(ndjson_files)} NDJSON files to load into BigQuery.")

# === Step 5: Load each NDJSON file into BigQuery ===
for uri in ndjson_files:
    try:
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND
        )
        load_job = bq_client.load_table_from_uri(
            uri,
            f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}",
            job_config=job_config
        )
        logger.info(f"Started BigQuery load job {load_job.job_id} for {uri}")
        load_job.result()  # Wait for job to complete
        logger.info(f"Loaded {uri} into {DATASET_ID}.{TABLE_ID}")
    except Exception as e:
        logger.error(f"Failed to load {uri} to BigQuery: {e}")
        raise

logger.info("BigQuery loading complete.")