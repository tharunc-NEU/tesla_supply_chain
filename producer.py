import requests
from kafka import KafkaProducer
import datetime
import time
import json
from dotenv import load_dotenv
import os

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Ensure JSON serialization
)

# Kafka topic
topic = 'supply_chain_news'

# Load environment variables from .env file
load_dotenv()

# Your NewsAPI key
api_key = os.getenv('NEWS_API_KEY')

# NewsAPI base URL
base_url = 'https://newsapi.org/v2/everything'

# Function to fetch news articles
def fetch_news():
    to_date = datetime.datetime.utcnow()
    from_date = to_date - datetime.timedelta(days=30)

    params = {
        'q': 'supply chain OR logistics OR procurement OR shipping',
        'from': from_date.isoformat(),
        'to': to_date.isoformat(),
        'sortBy': 'publishedAt',
        'language': 'en',
        'apiKey': api_key
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        if not articles:
            print("No new articles found.")
            return

        for article in articles:
            # Prepare the message as a Python dictionary
            message = {
                'title': article.get('title', 'No Title'),
                'description': article.get('description', 'No Description'),
                'url': article.get('url', 'No URL'),
                'publishedAt': article.get('publishedAt', datetime.datetime.utcnow().isoformat())
            }
            producer.send(topic, value=message)
            print(f"Sent: {message}")

    except Exception as e:
        print(f"Error fetching news: {e}")

# Periodically fetch news
while True:
    print("Fetching news...")
    fetch_news()
    print("Waiting for the next interval...")
    time.sleep(10)
