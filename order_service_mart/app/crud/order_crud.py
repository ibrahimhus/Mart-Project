from app.models.order_model import Order, UpdatedOrder
from sqlmodel import Session, select  
from fastapi import HTTPException 

# Add a New Product to the Database
def add_new_order(order_data:Order, session:Session):
    session.add(order_data)
    session.commit()
    session.refresh(order_data)
    return order_data

# Get All Produts from the DB.
def get_all_orders(session:Session):
    all_orders = session.exec(select(Order)).all()
    return all_orders

# Get a Product by ID
def get_order_by_id(order_id:int, session:Session):
    order = session.exec(select(Order).where(Order.id == order_id)).one_or_none() 
    if order is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return order

# Delete Product by ID
def delete_order_by_id(order_id:int, session:Session):
    order = session.exec(select(Order).where(Order.id == order_id)).one_or_none() 
    if order is None:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(order)
    session.commit()
    return {'message': "Product deleted successfully"}

# Update Product by ID
def update_order_by_id(order_id: int, to_update_order_data:UpdatedOrder, session: Session):
    # Step 1: Get the Product by ID
    order = session.exec(select(Order).where(Order.id == order_id)).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Product not found")
    # Step 2: Update the Product
    hero_data = to_update_order_data.model_dump(exclude_unset=True)
    order.sqlmodel_update(hero_data)
    session.add(order)
    session.commit()
    return order

# Validate Product by ID

def validate_order_by_id(order_id: int, session: Session) -> Order | None:
    id_order = session.exec(select(Order).where(Order.id == order_id)).one_or_none()
    return id_order