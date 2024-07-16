# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from app import settings
from sqlmodel import Session, SQLModel, select
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer
import asyncio
import json



from app.consumer.order_cosumer import consume_message
from app.db import engine
from app.models.order_model import Order, UpdatedOrder
from app.crud.order_crud import add_new_order, get_all_orders, get_order_by_id, delete_order_by_id, update_order_by_id
from app.dep import get_kafka_producer, get_session




def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables.......")
    task = asyncio.create_task(consume_message("AddOrder", 'broker:19092'))
    create_db_and_tables()
    yield



app = FastAPI(lifespan=lifespan, title="Husnain API with DB", 
    version="0.0.1")



@app.get("/")
def read_root():
    return {"Hello": "Batch 47"}

# Kafka Producer as a dependency

@app.post("/manage-order/", response_model=Order)
#   """Create a new product and send it to Kafka"""
async def new_order (order: Order, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]) -> Order: 
    # session.add(order)    
    # session.commit()
    # session.refresh(order)
    # return product
    order_dict = {field: getattr(order, field) for field in order.dict()}
    order_json = json.dumps(order_dict).encode("utf-8")
    print("product_JSON:", order_json)
    # Produce message
    await producer.send_and_wait("AddOrder", order_json)
    # _product = add_new_product(product, session)
    return order

@app.get("/orders/", response_model=list[Order])
def get_order(session: Annotated[Session, Depends(get_session)]):
    """Get all orders"""
    return get_all_orders(session)


@app.get("/orders/{order_id}", response_model=Order)
def get_single_order(order_id: int, session: Annotated[Session, Depends(get_session)]):
    """Get a single order by ID"""
    try:
        return get_order_by_id(product_id=order_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
@app.delete("/orders/{order_id}", response_model=Order)
def delete_order(order_id: int, session: Annotated[Session, Depends(get_session)]):
    """delete a single order by ID"""
    order = session.exec(select().where(Order.id == order_id)).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(order)
    session.commit()
    return  {"message": "Order deleted successfully"}

# update product by ID
@app.patch("/manage-orders/{order_id}", response_model=Order)
def update_single_order(order_id: int, order: UpdatedOrder, session: Annotated[Session, Depends(get_session)]):
    """ Update a single product by ID"""
    try:
        return update_order_by_id(order_id=order_id, to_update_order_data=order, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
