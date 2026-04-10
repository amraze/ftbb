#!/usr/bin/env python3
"""
Basketball PDF Parser with RabbitMQ and Redis Integration
Extracts: team names, abbreviations, player names, and jersey numbers
Stores results in Redis instead of local JSON files
"""

import json
import logging
from pathlib import Path
from datetime import datetime

from clients.rabbitmq_client import RabbitMQClient
from clients.redis_client import RedisClient
from services.pdf_parser import SimplifiedBasketballParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFExtractionService:
    def __init__(self):
        """Initialize service with Redis and RabbitMQ clients"""
        self.redis_client = None
        self.rabbitmq_client = None
        self._connect_clients()
    
    def _connect_clients(self):
        try:
            logger.info("Initializing Redis connection...")
            self.redis_client = RedisClient()
            
            logger.info("Initializing RabbitMQ connection...")
            self.rabbitmq_client = RabbitMQClient()
            self.rabbitmq_client.declare_infrastructure()
            
            logger.info("All clients connected successfully")
        except Exception as e:
            logger.error(f"Failed to initialize clients: {e}")
            raise
    
    def process_folder_event(self, folder_path: str, event_id: str, creation_date: str) -> dict:
        logger.info(f"Processing folder: {folder_path}")
        
        # Convert relative path from PdfWorker to absolute path from PdfExtractor
        current_dir = Path(__file__).parent
        pdfworker_downloads = current_dir.parent.parent / "PdfWorker" / "FTBB.PdfWorker" / "Downloads"
        folder_name = Path(folder_path).name
        actual_folder_path = pdfworker_downloads / folder_name
        
        logger.info(f"Looking for folder at: {actual_folder_path}")
        
        # Check if folder exists
        if not actual_folder_path.exists():
            logger.error(f"Folder not found: {actual_folder_path}")
            return {
                'success': False,
                'error': f'Folder not found: {actual_folder_path}',
                'event_id': event_id
            }
        
        # Find all PDF files in the folder
        pdf_files = list(actual_folder_path.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {actual_folder_path}")
            return {
                'success': False,
                'error': f'No PDF files found',
                'event_id': event_id,
                'pdf_count': 0
            }
        
        logger.info(f"Found {len(pdf_files)} PDF file(s)")
        
        # Store event metadata
        event_metadata = {
            'event_id': event_id,
            'folder_path': str(actual_folder_path),
            'creation_date': creation_date,
            'processing_date': datetime.now().isoformat(),
            'pdf_count': len(pdf_files)
        }
        self.redis_client.store_event_metadata(event_id, event_metadata)
        
        # Track success/failure
        success_count = 0
        fail_count = 0
        teams_stored = 0
        
        # Process each PDF file independently
        for pdf_file in pdf_files:
            logger.info(f"Processing: {pdf_file.name}")
            
            try:
                # Parse PDF
                parser = SimplifiedBasketballParser(str(pdf_file))
                game_data = parser.parse()
                
                if game_data and game_data.get("teams"):
                    # Log extraction method
                    method = "OCR" if parser.used_ocr else "text extraction"
                    logger.info(f"Extraction method: {method}")
                    
                    # Store entire extraction result
                    self.redis_client.store_extraction_result(
                        game_data,
                        event_id,
                        pdf_file.name
                    )
                    
                    # Store each team separately for easy access
                    for team in game_data.get("teams", []):
                        team_name = team.get('name', 'Unknown')
                        team_abbr = team.get('abbreviation', 'UNKNOWN')
                        player_count = len(team.get('players', []))
                        
                        # Store team data in Redis
                        self.redis_client.store_team_data(
                            team,
                            team_abbr,
                            event_id
                        )
                        
                        logger.info(
                            f"✓ Stored: {team_name} ({team_abbr}) - {player_count} player(s)"
                        )
                        teams_stored += 1
                    
                    success_count += 1
                else:
                    logger.error(f"Failed to extract data from {pdf_file.name} - No valid data found")
                    fail_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to extract data from {pdf_file.name}: {e}", exc_info=True)
                fail_count += 1
                continue
        
        # Prepare result
        result = {
            'success': success_count > 0,
            'event_id': event_id,
            'pdf_processed': success_count,
            'teams_stored': teams_stored,
            'failed': fail_count,
            'total_pdf': len(pdf_files)
        }
        
        # Log summary
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing complete!")
        logger.info(f"  ✓ PDFs processed: {success_count}")
        logger.info(f"  ✓ Teams stored in Redis: {teams_stored}")
        logger.info(f"  ✗ Failed: {fail_count} file(s)")
        logger.info(f"{'='*50}\n")
        
        return result
    
    def message_callback(self, ch, method, properties, body):
        logger.info(f"\n{'='*50}")
        logger.info(f"Event Received!")
        logger.info(f"{'='*50}")
        
        try:
            # Parse the message
            message = json.loads(body)
            logger.info(f"Message Content (JSON):")
            logger.info(json.dumps(message, indent=2))
            
            # Extract folder information
            folder_path = message.get('FolderPath')
            event_id = message.get('Id')
            creation_date = message.get('CreationDate')
            
            if folder_path and event_id:
                # Process the folder and store results in Redis
                result = self.process_folder_event(
                    folder_path,
                    event_id,
                    creation_date or datetime.now().isoformat()
                )
                
                logger.info(f"Processing result: {json.dumps(result, indent=2)}")
            else:
                logger.error("ERROR: FolderPath or Id not found in message")
            
        except json.JSONDecodeError:
            logger.error(f"Could not parse message as JSON")
            logger.error(f"Message Content (Raw): {body.decode('utf-8')}")
        except Exception as e:
            logger.error(f"ERROR processing message: {e}", exc_info=True)
        
        logger.info(f"Routing Key: {method.routing_key}")
        logger.info(f"Exchange: {method.exchange}")
        logger.info(f"Delivery Tag: {method.delivery_tag}")
        logger.info(f"{'='*50}\n")
        
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def start(self):
        """Start listening for messages"""
        try:
            logger.info(f"Starting PDF Extraction Service")
            logger.info(f"{'='*50}")
            logger.info(f"✓ Redis backend enabled")
            logger.info(f"✓ Listening to RabbitMQ queue")
            logger.info(f"{'='*50}\n")
            
            self.rabbitmq_client.start_consuming(self.message_callback)
        except KeyboardInterrupt:
            logger.info("\nShutting down gracefully...")
        except Exception as e:
            logger.error(f"Service error: {e}", exc_info=True)
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if self.rabbitmq_client:
                self.rabbitmq_client.close()
            if self.redis_client:
                self.redis_client.close()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def main():
    """Main entry point"""
    try:
        service = PDFExtractionService()
        service.start()
    except Exception as e:
        logger.error(f"Failed to start service: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()
    
    def to_json(self, output_path: str = None, indent: int = 2) -> str:
        """Convert parsed data to JSON"""
        json_str = json.dumps(self.data, indent=indent, ensure_ascii=False)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)
        
        return json_str


def process_folder_event(folder_path, event_id, creation_date):
    print(f"\nProcessing folder: {folder_path}")
    
    # Convert relative path from PdfWorker to absolute path from PdfExtractor
    current_dir = Path(__file__).parent
    pdfworker_downloads = current_dir.parent.parent / "PdfWorker" / "FTBB.PdfWorker" / "Downloads"
    folder_name = Path(folder_path).name
    actual_folder_path = pdfworker_downloads / folder_name
    
    print(f"Looking for folder at: {actual_folder_path}")
    
    # Check if folder exists
    if not actual_folder_path.exists():
        print(f"ERROR: Folder not found: {actual_folder_path}")
        return
    
    # Find all PDF files in the folder
    pdf_files = list(actual_folder_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {actual_folder_path}")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s)")
    
    # Create output directory for JSONs if it doesn't exist
    output_dir = Path("./extracted_data")
    output_dir.mkdir(exist_ok=True)
    
    # Track success/failure
    success_count = 0
    fail_count = 0
    teams_created = 0
    
    # Process each PDF file independently
    for pdf_file in pdf_files:
        print(f"\n  Processing: {pdf_file.name}")
        
        try:
            # Use the simplified basketball parser
            parser = SimplifiedBasketballParser(str(pdf_file))
            game_data = parser.parse()
            
            if game_data and game_data.get("teams"):
                # Print summary
                method = "OCR" if parser.used_ocr else "text extraction"
                print(f"    Method: {method}")
                
                # Create separate JSON file for each team
                for team in game_data.get("teams", []):
                    team_name = team.get('name', 'Unknown')
                    team_abbr = team.get('abbreviation', 'UNKNOWN')
                    player_count = len(team.get('players', []))
                    
                    # Create filename from team abbreviation
                    base_filename = f"{team_abbr}.json"
                    json_path = output_dir / base_filename
                    
                    # Handle duplicates - add number suffix if file exists
                    counter = 1
                    while json_path.exists():
                        json_path = output_dir / f"{team_abbr}_{counter}.json"
                        counter += 1
                    
                    # Create single-team JSON structure
                    team_data = {
                        "name": team_name,
                        "abbreviation": team_abbr,
                        "players": team.get('players', [])
                    }
                    
                    # Write JSON file
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(team_data, f, indent=2, ensure_ascii=False)
                    
                    print(f"    ✓ Created: {json_path.name}")
                    print(f"      {team_name} ({team_abbr}): {player_count} player(s)")
                    teams_created += 1
                
                success_count += 1
            else:
                print(f"  ✗ Failed to extract data from {pdf_file.name} - No valid data found")
                fail_count += 1
                
        except Exception as e:
            print(f"  ✗ Failed to extract data from {pdf_file.name}")
            print(f"    Error: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1
            continue
    
    print(f"\n{'='*50}")
    print(f"Processing complete!")
    print(f"  ✓ PDFs processed: {success_count}")
    print(f"  ✓ Team files created: {teams_created}")
    print(f"  ✗ Failed: {fail_count} file(s)")
    print(f"{'='*50}\n")


def callback(ch, method, properties, body):
    print(f"\n{'='*50}")
    print(f"Event Received!")
    print(f"{'='*50}")
    
    try:
        # Parse the message
        message = json.loads(body)
        print(f"Message Content (JSON):")
        print(json.dumps(message, indent=2))
        
        # Extract folder information
        folder_path = message.get('FolderPath')
        event_id = message.get('Id')
        creation_date = message.get('CreationDate')
        
        if folder_path:
            # Process the folder and create JSONs for each PDF
            process_folder_event(folder_path, event_id, creation_date)
        else:
            print("ERROR: FolderPath not found in message")
        
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse message as JSON")
        print(f"Message Content (Raw): {body.decode('utf-8')}")
    except Exception as e:
        print(f"ERROR processing message: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nRouting Key: {method.routing_key}")
    print(f"Exchange: {method.exchange}")
    print(f"Delivery Tag: {method.delivery_tag}")
    print(f"{'='*50}\n")
    
    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    """Main RabbitMQ connection and consumer setup"""
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
    
    # Declare exchange as TOPIC
    channel.exchange_declare(
        exchange=Config.EXCHANGE_NAME,
        exchange_type='topic',
        durable=True
    )
    
    # Declare queue
    channel.queue_declare(
        queue=Config.QUEUE_NAME,
        durable=True
    )
    
    # Bind queue to exchange
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