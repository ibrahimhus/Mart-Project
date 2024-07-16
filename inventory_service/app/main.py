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
from app.models.inventory_model import InventoryItem
from app.crud.inventory_crud import get_all_inventorys, get_inventory_by_id, delete_inventory_by_id
from app.dep import get_kafka_producer, get_session
from app.Consumer.add_stock_consumer import consume_message



def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables......")
    task = asyncio.create_task(consume_message("inventory-add-stock-response", 'broker:19092'))
    create_db_and_tables()
    print ("\n\n lifespan started \n\n ")
    yield



app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1")



@app.get("/")
def read_root():
    return {"Hello": "Batch 47"}

# Kafka Producer as a dependency

@app.post("/manage-INV/", response_model=InventoryItem)
#   """Create a new product and send it to Kafka"""
async def new_inventory (inventory: InventoryItem, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]) -> InventoryItem: 
    



    inventory_dict = {field: getattr(inventory, field) for field in inventory.dict()}
    inventory_json = json.dumps(inventory_dict).encode("utf-8")
    print("iventory_JSON:", inventory_json)
    # # # Produce message
    await producer.send_and_wait("Addstock", inventory_json)
    # _product = add_new_inventory(inventory, session)
    return inventory

@app.get("/iventories/", response_model=list[InventoryItem])
def get_inv(session: Annotated[Session, Depends(get_session)]):
    """Get all products"""
    return get_all_inventorys(session)


@app.get("/iventories/{inventory_id}", response_model=InventoryItem)
def get_single_inventory(inventory_id: int, session: Annotated[Session, Depends(get_session)]):
    """Get a single product by ID"""
    try:
        return get_inventory_by_id(inventory_id=inventory_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
@app.delete("/inventories/{inventory_id}", response_model=InventoryItem)
def delete_inventory(inventory_id: int, session: Annotated[Session, Depends(get_session)]):
    """delete a single product by ID"""
    try:
        return delete_inventory_by_id(inventory_id=inventory_id, session=session)
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
