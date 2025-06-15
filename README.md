# Stock Data Analytics Pipeline - June 2025

![Stock Dashboard](https://via.placeholder.com/800x400.png?text=Stock+Data+Analytics+Dashboard)  
*An interactive stock data analytics pipeline built with Kafka, BigQuery, Looker Studio, and Dash.*

## 📋 Project Overview

This project builds an end-to-end stock data analytics pipeline to process, store, and visualize stock market data. The pipeline ingests stock data from a CSV file, streams it via Kafka, stores it in Google Cloud Storage (GCS) as NDJSON files, loads it into BigQuery, and visualizes it using two dashboards: one in Looker Studio and another using Flask and Dash.

### Key Features
- **Data Source**: Stock data from `indexProcessed.csv` (e.g., `GSPTSE`, `IXIC` indices with columns: `Index`, `Date`, `Open`, `High`, `Low`, `Close`, `Volume`).
- **Streaming**: Kafka streams data to a `stock-data` topic.
- **Storage**: NDJSON files in GCS (`/`).
- **Database**: BigQuery table (`` with 15610 records).
- **Visualization**:
  - Looker Studio dashboard with line charts, bar charts, tables, and scorecards.
  - Flask and Dash dashboard with interactive candlestick, line, and bar charts.
- **Deployment**: Options for free hosting on Heroku, Render, Fly.io, etc.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Google Cloud SDK (for BigQuery and GCS access)
- Kafka (local or cloud setup)
- Dependencies:
  ```bash
  pip install kafka-python google-cloud-storage google-cloud-bigquery pandas dash flask plotly pandas-gbq gunicorn
  ```

### Directory Structure
```
stock-data-pipeline/
├── config/
│   └── kafka_config.py        # Configuration file for GCS, BigQuery, Kafka
├── scripts/
│   ├── kafka_producer_consumer_with_json_upload.py  # Kafka producer/consumer script
│   ├── load_to_bigquery.py    # Script to load NDJSON to BigQuery
│   └── app.py                 # Flask and Dash dashboard
├── keys/
│   └── stockstream-service-account-key.json  # GCP service account key
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
└── Procfile                   # For Heroku/Render deployment
```

### Setup Instructions
1. **Clone the Repository** (if using Git):
   ```bash
   git clone https://github.com/FaheemKhan0817/Stock-Data-Analytics-Pipeline.git
   cd Stock-Data-Analytics-Pipeline
   ```

2. **Set Up Google Cloud Credentials**:
   - Place your service account key (`stockstream-service-account-key.json`) in the `keys/` directory.
   - Update `config/kafka_config.py` with your configurations:
     ```python
     GOOGLE_APPLICATION_CREDENTIALS = os.path.abspath('keys/stockstream-service-account-key.json')
     BUCKET_NAME = ''
     KAFKA_BOOTSTRAP_SERVERS = ''
     KAFKA_TOPIC = ''
     KAFKA_GROUP_ID = ''
     ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Kafka Pipeline**:
   - Start Kafka (if local):
     ```bash
     # Start Zookeeper
     zookeeper-server-start.sh config/zookeeper.properties
     # Start Kafka server
     kafka-server-start.sh config/server.properties
     ```
   - Run the producer/consumer script:
     ```bash
     python scripts/kafka_producer_consumer_with_json_upload.py
     ```
   - This will stream data from `indexProcessed.csv`, save NDJSON files to GCS, and log progress.

5. **Load Data into BigQuery**:
   ```bash
   python scripts/load_to_bigquery.py
   ```
   - This loads NDJSON files from GCS into `stock_data_analytics.stock_stream_table`.

## 📊 Visualizations

### Looker Studio Dashboard
- **Access**: [Link to your Looker Studio dashboard](https://lookerstudio.google.com/reporting/0e249b43-9518-4186-b2df-1242a4c8caa3)
- **Features**:
  - **Line Chart**: Closing price trends over time.
  - **Bar Chart**: Total volume by index.
  - **Table**: Summary metrics (average close, total volume) by index.
  - **Scorecards**: Total volume and latest closing price.
  - **Interactivity**: Filter by `Index` and date range.

### Flask and Dash Dashboard
- **Run Locally**:
  ```bash
  python scripts/app.py
  ```
  - Access at `http://127.0.0.1:8050/`.
- **Features**:
  - **Candlestick Chart**: Shows `Open`, `High`, `Low`, `Close` for a selected index.
  - **Line Chart**: Closing price trends over time.
  - **Bar Chart**: Total volume by index.
  - **Interactivity**: Dropdown for `Index`, date range picker.

<!-- ## 🌐 Deployment

### Free Hosting Options (Without GCP)
1. **Heroku** (Recommended):
   - Create a `Procfile`:
     ```
     web: gunicorn app:server
     ```
   - Deploy:
     ```bash
     heroku create your-app-name
     git push heroku main
     ```
   - Access at `https://your-app-name.herokuapp.com`.

2. **Render**:
   - Set up a web service with build command `pip install -r requirements.txt` and start command `gunicorn app:server`.
   - Access at `https://yourapp.onrender.com`.

3. **Fly.io**:
   - Use `flyctl launch` and `flyctl deploy`.
   - Access at `https://yourapp.fly.dev`. -->

### Notes
- Free tiers may have limitations (e.g., app sleeping after inactivity, limited hours).
- Securely add your GCP credentials as environment variables (e.g., `heroku config:set GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`).

## 📈 Future Improvements
- Add error handling and logging for robustness.
- Aggregate data in BigQuery for faster dashboard performance.
- Dockerize the pipeline for portability (Phase 6).

## 📧 Contact
For questions or feedback, reach out via LinkedIn: [Your LinkedIn Profile](https://linkedin.com/in/faheemkhanml).

---

*Built with 💡 by Faheem Khan on June 15, 2025.*