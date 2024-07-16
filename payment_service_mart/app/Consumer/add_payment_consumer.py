from aiokafka import AIOKafkaConsumer
from app.dep import get_session
from app.crud.payment_crud import add_new_payment
import json
from app.models.payment_model import Payment


async def consume_message(topic, bootstrap_servers):
# create a consumer instance
    consumer = AIOKafkaConsumer(
        topic, 
        bootstrap_servers= bootstrap_servers,
        group_id = "payment-service-consumer-group"
    )
    await consumer.start()
    try:
        async for message in consumer:
            print("RAW ADD PAYMENT MESSAGE")
            print(f"Received message on topic {message.topic}")
             
            payment_data = json.loads(message.value.decode())
            print("Type", type(payment_data))
            print(f"inventory_data {payment_data}") 

            with next(get_session()) as session:
                db_payment = add_new_payment(payment_data=Payment(**payment_data), session=session)
                print("db_add_stock", db_payment)

    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()
