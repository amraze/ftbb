"""
RabbitMQ client wrapper for message handling
"""
import json
import logging
from typing import Callable, Optional
import pika

from config.rabbitmq_config import RabbitMQConfig

logger = logging.getLogger(__name__)


class RabbitMQClient:
    """Wrapper for RabbitMQ connection and operations"""
    
    def __init__(self):
        """Initialize RabbitMQ connection"""
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(
                RabbitMQConfig.USER,
                RabbitMQConfig.PASSWORD
            )
            
            parameters = pika.ConnectionParameters(
                host=RabbitMQConfig.HOST,
                port=RabbitMQConfig.PORT,
                virtual_host=RabbitMQConfig.VHOST,
                credentials=credentials,
                heartbeat=RabbitMQConfig.HEARTBEAT,
                blocked_connection_timeout=RabbitMQConfig.BLOCKED_CONNECTION_TIMEOUT
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            logger.info(f"RabbitMQ connected to {RabbitMQConfig.HOST}:{RabbitMQConfig.PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def declare_infrastructure(self):
        """Declare exchange and queue"""
        try:
            # Declare exchange
            self.channel.exchange_declare(
                exchange=RabbitMQConfig.EXCHANGE_NAME,
                exchange_type=RabbitMQConfig.EXCHANGE_TYPE,
                durable=RabbitMQConfig.DURABLE_EXCHANGE
            )
            logger.info(f"Exchange declared: {RabbitMQConfig.EXCHANGE_NAME}")
            
            # Declare queue
            self.channel.queue_declare(
                queue=RabbitMQConfig.QUEUE_NAME,
                durable=RabbitMQConfig.DURABLE_QUEUE
            )
            logger.info(f"Queue declared: {RabbitMQConfig.QUEUE_NAME}")
            
            # Bind queue to exchange
            self.channel.queue_bind(
                exchange=RabbitMQConfig.EXCHANGE_NAME,
                queue=RabbitMQConfig.QUEUE_NAME,
                routing_key=RabbitMQConfig.BINDING_KEY
            )
            logger.info(f"Queue bound to exchange with key: {RabbitMQConfig.BINDING_KEY}")
            
        except Exception as e:
            logger.error(f"Failed to declare infrastructure: {e}")
            raise
    
    def start_consuming(self, callback: Callable):
        """Start consuming messages from queue"""
        try:
            self.channel.basic_qos(prefetch_count=RabbitMQConfig.PREFETCH_COUNT)
            self.channel.basic_consume(
                queue=RabbitMQConfig.QUEUE_NAME,
                on_message_callback=callback
            )
            
            logger.info(f"Listening to queue: {RabbitMQConfig.QUEUE_NAME}")
            logger.info("Waiting for messages... Press CTRL+C to exit")
            
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"Error during consuming: {e}")
            raise
    
    def stop_consuming(self):
        """Stop consuming messages"""
        try:
            if self.channel:
                self.channel.stop_consuming()
                logger.info("Stopped consuming messages")
        except Exception as e:
            logger.error(f"Error stopping consumer: {e}")
    
    def publish_message(self, message: dict, routing_key: str = None,
                       exchange: str = None) -> bool:
        """Publish a message to the exchange"""
        try:
            exchange = exchange or RabbitMQConfig.EXCHANGE_NAME
            routing_key = routing_key or RabbitMQConfig.BINDING_KEY
            
            message_json = json.dumps(message, ensure_ascii=False)
            
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message_json,
                properties=pika.BasicProperties(
                    content_type='application/json',
                    delivery_mode=2  # Make message persistent
                )
            )
            
            logger.info(f"Message published to {exchange} with key {routing_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False
    
    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")
