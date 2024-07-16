# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel, select
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer
import asyncio
import json


from app.db import engine
from app.models.notification_model import Notification
from app.crud.notification_crud import get_notification_by_id, delete_notification_by_id, get_all_notifications
from app.dep import get_kafka_producer, get_session
from app.Consumer.add_notification_consumer import consume_message



def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables......")
    # task = asyncio.create_task(consume_message("UserOrder", 'broker:19092'))
    create_db_and_tables()
    print ("\n\n lifespan started \n\n ")
    yield



app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1")



@app.get("/")
def read_root():
    return {"Hello": "Batch 47"}

# Kafka Producer as a dependency

@app.post("/manage-notification/", response_model=Notification)
#   """Create a new user and send it to Kafka"""
async def new_user (notification: Notification, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]) -> Notification: 
    
    notification_dict = {field: getattr(notification, field) for field in notification.dict()}
    notification_json = json.dumps(notification_dict).encode("utf-8")
    print("notification_JSON:", notification_json)
    # # # Produce message
    await producer.send_and_wait("Notification", notification_json)
    # _product = add_new_inventory(inventory, session)
    return notification

@app.get("/notifications/", response_model=list[Notification])
def get_notification(session: Annotated[Session, Depends(get_session)]):
    """Get all notifications"""
    return get_all_notifications(session)


@app.get("/notifications/{notification_id}", response_model=Notification)
def get_single_notification(notification_id: int, session: Annotated[Session, Depends(get_session)]):
    """Get a Notification User by ID"""
    try:
        return get_notification_by_id(notification_id=notification_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
@app.delete("/notifications/{notification_id}", response_model=Notification)
def delete_notification(notification_id: int, session: Annotated[Session, Depends(get_session)]):
    """delete a single Notification by ID"""
    try:
        return delete_notification_by_id(notification_id=notification_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# update product by ID
# @app.patch("/manage-products/{product_id}", response_model=Product)
# def update_single_product(product_id: int, product: Updatedproducts, session: Annotated[Session, Depends(get_session)]):
#     """ Update a single product by ID"""
#     try:
#         return update_product_by_id(product_id=product_id, to_update_product_data=product, session=session)
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
