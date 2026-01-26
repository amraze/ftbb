import pika
import json
from config import Config

def callback(ch, method, properties, body):
    """
    Callback function that gets triggered when a message is received
    """
    print(f"\n{'='*50}")
    print(f"Event Received!")
    print(f"{'='*50}")
    
    try:
        # Try to parse as JSON for prettier printing
        message = json.loads(body)
        print(f"Message Content (JSON):")
        print(json.dumps(message, indent=2))
    except json.JSONDecodeError:
        # If not JSON, print as string
        print(f"Message Content (Raw):")
        print(body.decode('utf-8'))
    
    print(f"\nRouting Key: {method.routing_key}")
    print(f"Exchange: {method.exchange}")
    print(f"Delivery Tag: {method.delivery_tag}")
    print(f"{'='*50}\n")
    
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    # Create connection credentials
    credentials = pika.PlainCredentials(
        Config.RABBITMQ_USER,
        Config.RABBITMQ_PASSWORD
    )
    
    # Create connection parameters
    parameters = pika.ConnectionParameters(
        host=Config.RABBITMQ_HOST,
        port=Config.RABBITMQ_PORT,
        virtual_host=Config.RABBITMQ_VHOST,
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    
    # Establish connection
    print(f"Connecting to RabbitMQ at {Config.RABBITMQ_HOST}:{Config.RABBITMQ_PORT}...")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Declare exchange as TOPIC (not fanout) to match your C# code
    channel.exchange_declare(
        exchange=Config.EXCHANGE_NAME,
        exchange_type='topic',  # Changed from 'topic' - this is correct
        durable=True
    )
    
    # Declare queue (idempotent operation)
    channel.queue_declare(
        queue=Config.QUEUE_NAME,
        durable=True
    )
    
    # Bind queue to exchange
    # For topic exchange with empty routing key (like your C# code), use '#' to catch all
    binding_key = '#'
    channel.queue_bind(
        exchange=Config.EXCHANGE_NAME,
        queue=Config.QUEUE_NAME,
        routing_key=binding_key
    )
    
    print(f"Successfully connected!")
    print(f"Listening to queue: {Config.QUEUE_NAME}")
    print(f"Exchange: {Config.EXCHANGE_NAME} (topic)")
    print(f"Binding key: {binding_key}")
    print(f"\nWaiting for messages... Press CTRL+C to exit\n")
    
    # Set up consumer
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=Config.QUEUE_NAME,
        on_message_callback=callback
    )
    
    # Start consuming
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        channel.stop_consuming()
    finally:
        connection.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()