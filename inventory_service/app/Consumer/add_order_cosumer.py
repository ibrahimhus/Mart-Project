# main.py
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import json
from app.dep import get_session
from app.crud.product_crud import validate_product_by_id





async def consume_inventory_message(topic, bootstrap_servers):
# create a consumer instance
    consumer = AIOKafkaConsumer(
        topic, 
        bootstrap_servers= bootstrap_servers,
        group_id = "my-inventory_add_stock-consumer-group"
    )
    await consumer.start()
    try:
        async for message in consumer:
            print("\n\n RAW INVENTORY MESSAGE \n\n")
            print(f"\n\n Received message on topic {message.topic}")
            print(f"\n\n Message Value {message.value}")
             
            # Extract product ID
            inven_data = json.loads(message.value.decode())
            product_id = inven_data["product_id"]
            print("INVENTORY DATA PRODUCT ID", product_id) 
            
            # Check if Product ID is Valid
            with next(get_session()) as session:
                product_inventory = validate_product_by_id(product_id=product_id, session=session)
                print("Product Validation Check", product_inventory )

                # Add Stock
                if product_inventory is not None:

                    print("PRODUCT VALIDATION NOT NONE")

                    producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
                    await producer.start()
                    print("Producer Started")
                    try:
                        await producer.send_and_wait("inventory-add-stock-response", message.value)
                    finally:
                        await producer.stop()

                    continue
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()
