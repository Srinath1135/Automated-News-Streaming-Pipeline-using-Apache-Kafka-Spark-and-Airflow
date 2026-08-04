import os
from datetime import timedelta
import pendulum
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

# Path Definitions
DAGS_FOLDER = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = os.path.dirname(DAGS_FOLDER)
PYTHON_BIN = os.path.join(PROJECT_PATH, 'myenv', 'bin', 'python3')
# Set timezone to IST (India)
local_tz = pendulum.timezone("Asia/Kolkata")

default_args = {
    'owner': 'srinath',
    'depends_on_past': False,
    'start_date': pendulum.datetime(2025, 5, 27, tz=local_tz),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'news_aggregator',
    default_args=default_args,
    description='Stream AI news to Kafka, process with PySpark, and send email digests',
    schedule='0 9 * * *',  # 9:00 AM every day
    catchup=False,
) as dag:

    # Task 1: Publish news feeds to Kafka (using producer_agent.py from your folder)
    publish_to_kafka = BashOperator(
        task_id='publish_to_kafka',
        bash_command=f'cd "{PROJECT_PATH}" && {PYTHON_BIN} producer_agent.py',
    )

    # Task 2: Process Kafka batch data with PySpark
    process_with_spark = BashOperator(
        task_id='process_with_spark',
        bash_command=f'cd "{PROJECT_PATH}" && {PYTHON_BIN} spark_processor.py',
    )

    # Task 3: Send personalized HTML email digests
    send_emails = BashOperator(
        task_id='send_emails',
        bash_command=f'cd "{PROJECT_PATH}" && {PYTHON_BIN} email_agent.py --send',
    )

    # Task Dependencies
    publish_to_kafka >> process_with_spark >> send_emails
