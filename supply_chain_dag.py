from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

# Default arguments for the DAG
default_args = {
    'owner': 'tharun',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define Python functions to run producer and consumer scripts
def run_producer():
    """Runs the producer script."""
    subprocess.run(["python", "producer.py"], check=True)

def run_consumer():
    """Runs the consumer script."""
    subprocess.run(["python", "consumer.py"], check=True)

# Define the DAG
with DAG(
    'supply_chain_workflow',
    default_args=default_args,
    description='Fetch news from NewsAPI, process with Kafka, and store in MySQL',
    schedule_interval=timedelta(hours=1),  # Run every hour
    start_date=datetime(2024, 11, 1),
    catchup=False,
) as dag:

    # Define tasks
    producer_task = PythonOperator(
        task_id='run_producer',
        python_callable=run_producer,
    )

    consumer_task = PythonOperator(
        task_id='run_consumer',
        python_callable=run_consumer,
    )

    # Set dependencies
    producer_task >> consumer_task
