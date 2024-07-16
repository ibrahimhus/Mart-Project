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
from app.models.user_model import User
from app.crud.user_crud import get_all_users, get_user_by_id, delete_user_by_id
from app.dep import get_kafka_producer, get_session
from app.Consumer.add_user_consumer import consume_message



def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables......")
    task = asyncio.create_task(consume_message("UserOrder", 'broker:19092'))
    create_db_and_tables()
    print ("\n\n lifespan started \n\n ")
    yield



app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1")



@app.get("/")
def read_root():
    return {"Hello": "Batch 47"}

# Kafka Producer as a dependency

@app.post("/manage-user/", response_model=User)
#   """Create a new user and send it to Kafka"""
async def new_user (user: User, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]) -> User: 
    
    user_dict = {field: getattr(user, field) for field in user.dict()}
    user_json = json.dumps(user_dict).encode("utf-8")
    print("iventory_JSON:", user_json)
    # # # Produce message
    await producer.send_and_wait("UserOrder", user_json)
    # _product = add_new_inventory(inventory, session)
    return user

@app.get("/users/", response_model=list[User])
def get_user(session: Annotated[Session, Depends(get_session)]):
    """Get all users"""
    return get_all_users(session)


@app.get("/users/{user_id}", response_model=User)
def get_single_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    """Get a single User by ID"""
    try:
        return get_user_by_id(user_id=user_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    """delete a single User by ID"""
    try:
        return delete_user_by_id(payment_id=user_id, session=session)
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
