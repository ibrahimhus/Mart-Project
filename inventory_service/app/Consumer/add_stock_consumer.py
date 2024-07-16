from aiokafka import AIOKafkaConsumer
from app.dep import get_session
from app.crud.inventory_crud import add_new_inventory
import json
from app.models.inventory_model import InventoryItem




async def consume_message(topic, bootstrap_servers):
# create a consumer instance
    consumer = AIOKafkaConsumer(
        topic, 
        bootstrap_servers= bootstrap_servers,
        group_id = "inventory-add-stock-response"
    )
    await consumer.start()
    try:
        async for message in consumer:
            print("RAW ADD STOCK CONSUMER MESSAGE")
            print(f"Received message on topic {message.topic}")
             
            inventory_data = json.loads(message.value.decode())
            print("Type", type(inventory_data))
            print(f"inventory_data {inventory_data}") 

            with next(get_session()) as session:
                db_product = add_new_inventory(inventory_data=InventoryItem(**inventory_data), session=session)
                print("db_add_stock", db_product)

    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()
