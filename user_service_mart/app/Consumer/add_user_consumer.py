from aiokafka import AIOKafkaConsumer
from app.dep import get_session
from app.crud.user_crud import add_new_user
import json
from app.models.user_model import User


async def consume_message(topic, bootstrap_servers):
# create a consumer instance
    consumer = AIOKafkaConsumer(
        topic, 
        bootstrap_servers= bootstrap_servers,
        group_id = "user-service-consumer-group"
    )
    await consumer.start()
    try:
        async for message in consumer:
            print("RAW ADD PAYMENT MESSAGE")
            print(f"Received message on topic {message.topic}")
             
            user_data = json.loads(message.value.decode())
            print("Type", type(user_data))
            print(f"inventory_data {user_data}") 

            with next(get_session()) as session:
                db_user = add_new_user(user_data=User(**user_data), session=session)
                print("db_add_stock", db_user)

    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()
