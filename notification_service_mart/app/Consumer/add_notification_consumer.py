from aiokafka import AIOKafkaConsumer
from app.dep import get_session
from app.crud.notification_crud import add_new_notification
import json
from app.models.notification_model import Notification


async def consume_message(topic, bootstrap_servers):
# create a consumer instance
    consumer = AIOKafkaConsumer(
        topic, 
        bootstrap_servers= bootstrap_servers,
        group_id = "notification-service-consumer-group"
    )
    await consumer.start()
    try:
        async for message in consumer:
            print("RAW ADD NOTIFICATION MESSAGE")
            print(f"Received message on topic {message.topic}")
             
            notification_data = json.loads(message.value.decode())
            print("Type", type(notification_data))
            print(f"notification_data {notification_data}") 

            with next(get_session()) as session:
                db_notification = add_new_notification(user_data=Notification(**notification_data), session=session)
                print("db_add_stock", db_notification)

    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()
