import json
import time
from confluent_kafka import Producer
from backup_news_fetcher import BackupNewsFetcher
from entertainment_fetcher import EntertainmentFetcher

# Kafka configuration
conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"✅ Article delivered to {msg.topic()} [{msg.partition()}]")

def publish_news():
    print("📰 Fetching news feeds for Kafka streaming...")
    
    backup_fetcher = BackupNewsFetcher()
    entertainment_fetcher = EntertainmentFetcher()
    
    articles = []
    articles.extend(backup_fetcher.fetch_all_sources(limit_per_source=3))
    articles.extend(entertainment_fetcher.fetch_all_entertainment(limit_per_source=3))
    
    for article in articles:
        # Convert article dict to JSON string
        payload = json.dumps(article)
        
        # Publish to Kafka topic
        producer.produce(
            topic='raw-news-topic',
            key=article.get('platform', 'general'),
            value=payload,
            callback=delivery_report
        )
        producer.poll(0)
        time.sleep(0.1)
        
    producer.flush()
    print("🎉 All articles published to Kafka!")

if __name__ == "__main__":
    publish_news()
