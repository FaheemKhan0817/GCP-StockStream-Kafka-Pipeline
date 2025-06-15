import os
import json
import time
import sys
import tempfile
import pandas as pd
from kafka import KafkaProducer, KafkaConsumer
from google.cloud import storage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# === Config ===
from config.kafka_config import *

# Update SOURCE_BLOB_NAME to the new path (remove the bucket name part since it's already in BUCKET_NAME)
SOURCE_BLOB_NAME = 'Stock_data.csv'

# === Step 1: Set Google Cloud credentials ===
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS

# === Step 2: Initialize GCS client ===
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

# === Step 3: Download CSV from GCS ===
destination_file = os.path.join(tempfile.gettempdir(), os.path.basename(SOURCE_BLOB_NAME))
blob = bucket.blob(SOURCE_BLOB_NAME)
blob.download_to_filename(destination_file)
print(f'Downloaded gs://{BUCKET_NAME}/{SOURCE_BLOB_NAME} to {destination_file}')

# === Step 4: Read CSV file ===
df = pd.read_csv(destination_file)

# === Step 5: Randomly sample 60,00 records from the CSV ===
print(f"Total records in CSV: {len(df)}")
sample_size = min(6000, len(df))  # Ensure we don't sample more than the total records
df_sampled = df.sample(n=sample_size, random_state=42)  # random_state for reproducibility
print(f"Sampled {len(df_sampled)} records")

# === Step 6: Save sampled records to a JSON file ===
json_file = os.path.join(tempfile.gettempdir(), 'sampled_stock_data.json')
df_sampled.to_json(json_file, orient='records', lines=False)
print(f"Saved sampled data to {json_file}")

# === Step 7: Setup Kafka Producer ===
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# === Step 8: Produce sampled rows to Kafka ===
print("📤 Sending sampled data to Kafka...")
for _, row in df_sampled.iterrows():
    data = row.to_dict()
    producer.send(KAFKA_TOPIC, data)
    print(f"Sent: {data}")
    time.sleep(0.5)  # simulate streaming delay

producer.flush()
producer.close()

# === Step 9: Cleanup temp CSV file ===
os.remove(destination_file)
print(f"Removed temporary CSV file: {destination_file}")

# === Step 10: Setup Kafka Consumer ===
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id=KAFKA_GROUP_ID,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# === Step 11: Consume messages and write NDJSON to GCS ===
file_counter = 1
messages = []
print("📥 Consuming from Kafka and writing to GCS...")

for message in consumer:
    data = message.value
    messages.append(data)
    print(f"Received: {data}")

    if len(messages) >= 10:
        timestamp = time.strftime('%Y%m%d-%H%M%S')
        blob_name = f'stock-data-{timestamp}-{file_counter}.ndjson'
        ndjson_data = '\n'.join([json.dumps(msg) for msg in messages])
        blob = bucket.blob(blob_name)
        blob.upload_from_string(ndjson_data, content_type='application/x-ndjson')
        print(f"Wrote {len(messages)} messages to gs://{BUCKET_NAME}/{blob_name}")
        messages = []  # Reset the messages list
        file_counter += 1  # Increment file counter for the next batch