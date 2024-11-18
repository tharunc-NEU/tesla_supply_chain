from kafka import KafkaConsumer
import mysql.connector
import json
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
db_password = os.getenv('DB_PASSWORD')
# Connect to MySQL Database securely
db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password= db_password,  # Use password from environment variable
    database="supply_chain"
)
cursor = db_connection.cursor()

# Kafka Consumer
consumer = KafkaConsumer(
    'supply_chain_news',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='news_group'
)

# Function to store articles in MySQL
def store_article(article):
    try:
        # Convert publishedAt to MySQL-compatible datetime format
        published_at = article.get('publishedAt', None)
        if published_at:
            published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")  # Convert to Python datetime

        sql = """
        INSERT INTO articles (title, description, url, published_at)
        VALUES (%s, %s, %s, %s)
        """
        values = (
            article.get('title', 'No Title'),
            article.get('description', 'No Description'),
            article.get('url', 'No URL'),
            published_at
        )
        cursor.execute(sql, values)
        db_connection.commit()
        print(f"Stored article: {article['title']}")
    except Exception as e:
        print(f"Error storing article: {e}")

# Listen to Kafka and process messages
print("Listening to messages on Kafka topic...")
for message in consumer:
    raw_message = message.value.decode('utf-8')
    print(f"DEBUG: Raw message received: {raw_message}")

    try:
        # Attempt to parse JSON
        article = json.loads(raw_message)
        print(f"DEBUG: Converted to JSON: {article}")
        store_article(article)
    except json.JSONDecodeError as e:
        print(f"ERROR: Malformed message skipped: {raw_message}, Error: {e}")
    except Exception as e:
        print(f"ERROR: Failed to process message: {raw_message}, Error: {e}")

# Close the database connection after consuming
cursor.close()
db_connection.close()
