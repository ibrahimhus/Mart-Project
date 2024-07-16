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
from app.models.payment_model import Payment
from app.crud.payment_crud import get_all_payments, get_payment_by_id, delete_payment_by_id
from app.dep import get_kafka_producer, get_session
from app.Consumer.add_payment_consumer import consume_message



def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables......")
    task = asyncio.create_task(consume_message("PaymentOrder", 'broker:19092'))
    create_db_and_tables()
    print ("\n\n lifespan started \n\n ")
    yield



app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1")



@app.get("/")
def read_root():
    return {"Hello": "Batch 47"}

# Kafka Producer as a dependency

@app.post("/manage-PAYMENT/", response_model=Payment)
#   """Create a new product and send it to Kafka"""
async def new_payment (payment: Payment, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]) -> Payment: 
    
    pay_dict = {field: getattr(payment, field) for field in payment.dict()}
    payment_json = json.dumps(pay_dict).encode("utf-8")
    print("iventory_JSON:", payment_json)
    # # # Produce message
    await producer.send_and_wait("PaymentOrder", payment_json)
    # _product = add_new_inventory(inventory, session)
    return payment

@app.get("/payments/", response_model=list[Payment])
def get_payment(session: Annotated[Session, Depends(get_session)]):
    """Get all payments"""
    return get_all_payments(session)


@app.get("/paymentsID/{payment_id}", response_model=Payment)
def get_single_payment(payment_id: int, session: Annotated[Session, Depends(get_session)]):
    """Get a single payment by ID"""
    try:
        return get_payment_by_id(payment_id=payment_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
@app.delete("/payments/{payment_id}", response_model=Payment)
def delete_payment(payment_id: int, session: Annotated[Session, Depends(get_session)]):
    """delete a single payment by ID"""
    try:
        return delete_payment_by_id(payment_id=payment_id, session=session)
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
