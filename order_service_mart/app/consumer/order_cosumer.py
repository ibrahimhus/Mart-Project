# main.py
from aiokafka import AIOKafkaConsumer
import json
from app.models.order_model import Order
from app.crud.order_crud import add_new_order
from app.dep import get_session






async def consume_message(topic, bootstrap_servers):
# create a consumer instance
    consumer = AIOKafkaConsumer(
        topic, 
        bootstrap_servers= bootstrap_servers,
        group_id = "my-order-consumer-group"
    )
    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message: {
                  message.value.decode()} on topic {message.topic}") 
            order_data = json.loads(message.value.decode())
            print("Type", type(order_data))
            print(f"order_data {order_data}") 

            with next(get_session()) as session:
                db_order = add_new_order(order_data=Order(**order_data), session=session)
                print("db_product", db_order)

    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()
