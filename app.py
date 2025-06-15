import sys
import os
import pandas as pd
from pandas.io import gbq
from google.cloud import storage
from flask import Flask
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Add parent directory to sys.path to import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import configuration
from config.kafka_config import *

# Set Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS

# Initialize Flask app
server = Flask(__name__)

# Initialize Dash app
app = dash.Dash(__name__, server=server, url_base_pathname='/')

# Query BigQuery for stock data
PROJECT_ID = storage.Client().project
query = """
SELECT Index, Date, Open, High, Low, Close, Volume
FROM `stock_data_analytics.stock_stream_table`
ORDER BY Date
"""
df = gbq.read_gbq(query, project_id=PROJECT_ID)

# Convert Date column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Get unique indices for dropdown
indices = df['Index'].unique()

# Define the layout of the dashboard
app.layout = html.Div(
    style={'backgroundColor': '#FAFAFA', 'padding': '20px', 'fontFamily': 'Roboto'},
    children=[
        # Header
        html.H1(
            "Stock Data Analytics Dashboard - June 2025",
            style={'textAlign': 'center', 'color': '#1A73E8', 'fontSize': '24px', 'fontWeight': 'bold'}
        ),

        # Controls
        html.Div(
            style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'},
            children=[
                # Index Dropdown
                html.Div(
                    style={'width': '30%'},
                    children=[
                        html.Label("Select Index:", style={'fontSize': '14px', 'color': '#333'}),
                        dcc.Dropdown(
                            id='index-dropdown',
                            options=[{'label': idx, 'value': idx} for idx in indices],
                            value=indices[0],  # Default to first index
                            style={'fontSize': '12px', 'borderRadius': '5px'}
                        )
                    ]
                ),

                # Date Range Picker
                html.Div(
                    style={'width': '50%'},
                    children=[
                        html.Label("Select Date Range:", style={'fontSize': '14px', 'color': '#333'}),
                        dcc.DatePickerRange(
                            id='date-picker',
                            min_date_allowed=df['Date'].min(),
                            max_date_allowed=df['Date'].max(),
                            start_date=df['Date'].min(),
                            end_date=df['Date'].max(),
                            display_format='YYYY-MM-DD',
                            style={'fontSize': '12px', 'borderRadius': '5px'}
                        )
                    ]
                )
            ]
        ),

        # Visualizations
        html.Div(
            children=[
                # Candlestick Chart
                html.H2("Candlestick Chart", style={'fontSize': '18px', 'color': '#333'}),
                dcc.Graph(id='candlestick-chart', style={'height': '400px'}),

                # Line Chart
                html.H2("Closing Price Trends Over Time", style={'fontSize': '18px', 'color': '#333'}),
                dcc.Graph(id='line-chart', style={'height': '400px'}),

                # Bar Chart
                html.H2("Total Volume by Index", style={'fontSize': '18px', 'color': '#333'}),
                dcc.Graph(id='bar-chart', style={'height': '300px'}),
            ]
        )
    ]
)

# Define callback to update charts based on user input
@app.callback(
    [Output('candlestick-chart', 'figure'),
     Output('line-chart', 'figure'),
     Output('bar-chart', 'figure')],
    [Input('index-dropdown', 'value'),
     Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_charts(selected_index, start_date, end_date):
    # Filter data based on user input
    filtered_df = df[
        (df['Index'] == selected_index) &
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date)
    ]

    # Candlestick Chart
    candlestick_fig = go.Figure(data=[
        go.Candlestick(
            x=filtered_df['Date'],
            open=filtered_df['Open'],
            high=filtered_df['High'],
            low=filtered_df['Low'],
            close=filtered_df['Close'],
            name=selected_index
        )
    ])
    candlestick_fig.update_layout(
        title=f"{selected_index} Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template='plotly_white',
        margin=dict(l=50, r=50, t=50, b=50),
        font=dict(family="Roboto", size=12, color="#333")
    )

    # Line Chart
    line_fig = px.line(
        filtered_df,
        x='Date',
        y='Close',
        color='Index',
        title=f"{selected_index} Closing Price Trends Over Time"
    )
    line_fig.update_layout(
        template='plotly_white',
        margin=dict(l=50, r=50, t=50, b=50),
        font=dict(family="Roboto", size=12, color="#333")
    )
    line_fig.update_traces(line=dict(color='#1A73E8'))

    # Bar Chart
    bar_df = df[
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date)
    ].groupby('Index')['Volume'].sum().reset_index()
    bar_fig = px.bar(
        bar_df,
        x='Index',
        y='Volume',
        title="Total Volume by Index"
    )
    bar_fig.update_layout(
        template='plotly_white',
        margin=dict(l=50, r=50, t=50, b=50),
        font=dict(family="Roboto", size=12, color="#333")
    )
    bar_fig.update_traces(marker_color='#26A69A')

    return candlestick_fig, line_fig, bar_fig

# Run the Flask server
if __name__ == '__main__':
    server.run(debug=True, host='0.0.0.0', port=8050)