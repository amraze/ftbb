"""
RabbitMQ configuration module
"""
import os
from dotenv import load_dotenv

load_dotenv()


class RabbitMQConfig:
    HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    USER = os.getenv('RABBITMQ_USER', 'guest')
    PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    VHOST = os.getenv('RABBITMQ_VHOST', '/')
    
    # Queue configuration
    QUEUE_NAME = os.getenv('RABBITMQ_QUEUE_NAME', 'pdf_downloaded_queue')
    EXCHANGE_NAME = os.getenv('RABBITMQ_EXCHANGE_NAME', 'ftbb_event_bus')
    EXCHANGE_TYPE = 'topic'
    BINDING_KEY = os.getenv('RABBITMQ_BINDING_KEY', '#')
    
    # Connection settings
    HEARTBEAT = int(os.getenv('RABBITMQ_HEARTBEAT', 600))
    BLOCKED_CONNECTION_TIMEOUT = int(os.getenv('RABBITMQ_BLOCKED_TIMEOUT', 300))
    PREFETCH_COUNT = int(os.getenv('RABBITMQ_PREFETCH_COUNT', 1))
    
    # Message queue properties
    DURABLE_QUEUE = os.getenv('RABBITMQ_DURABLE_QUEUE', 'true').lower() == 'true'
    DURABLE_EXCHANGE = os.getenv('RABBITMQ_DURABLE_EXCHANGE', 'true').lower() == 'true'
