import sys
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType

# Force PySpark to download the Kafka connector before initializing
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 pyspark-shell'

# --- DYNAMIC PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "processed_spark_news")
CHECKPOINT_DIR = os.path.join(BASE_DIR, "spark_checkpoints")

def main():
    print("🚀 Starting PySpark Kafka Consumer...")

    # Initialize Spark Session with Kafka support
    spark = SparkSession.builder \
        .appName("AINewsSparkProcessor") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # Define Schema matching Kafka Producer payloads
    schema = StructType([
        StructField("title", StringType(), True),
        StructField("description", StringType(), True),
        StructField("source", StringType(), True),
        StructField("url", StringType(), True),
        StructField("published", StringType(), True),
        StructField("platform", StringType(), True)
    ])

    # Read Stream from Kafka
    raw_stream = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "raw-news-topic") \
        .option("startingOffsets", "earliest") \
        .load()

    # Parse JSON value from Kafka
    parsed_df = raw_stream \
        .selectExpr("CAST(value AS STRING) as json_payload") \
        .select(from_json(col("json_payload"), schema).alias("data")) \
        .select("data.*") \
        .withColumn("processed_at", current_timestamp())

    # Write processed data to JSON directory using dynamic paths
    query = parsed_df.writeStream \
        .format("json") \
        .option("path", PROCESSED_DIR) \
        .option("checkpointLocation", CHECKPOINT_DIR) \
        .outputMode("append") \
        .trigger(once=True) \
        .start()

    query.awaitTermination()
    print("✅ PySpark processing complete. Output saved to processed_spark_news/")

if __name__ == "__main__":
    main()
