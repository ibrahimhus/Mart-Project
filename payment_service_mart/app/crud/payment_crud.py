from app.models.payment_model import Payment
from sqlmodel import Session, select  
from fastapi import HTTPException 

# Add a New inventory to the Database
def add_new_payment(payment_data:Payment, session:Session):
    session.add(payment_data)
    session.commit()
    session.refresh(payment_data)
    return payment_data

# Get All inventory from the DB.
def get_all_payments(session:Session):
    all_payments = session.exec(select(Payment)).all()
    return all_payments

# Get a inventory by ID
def get_payment_by_id(payment_id:int, session:Session):
    payment = session.exec(select(Payment).where(Payment.id == payment_id)).one_or_none() 
    if payment is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return payment

# Delete Product by ID
def delete_payment_by_id(payment_id:int, session:Session):
    payment = session.exec(select(Payment).where(Payment.id == payment_id)).one_or_none() 
    if payment is None:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(payment)
    session.commit()
    return {'message': "Product deleted successfully"}

# Update Product by ID
# def update_product_by_id(product_id: int, to_update_product_data:Updatedproducts, session: Session):
#     # Step 1: Get the Product by ID
#     product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
#     if product is None:
#         raise HTTPException(status_code=404, detail="Product not found")
#     # Step 2: Update the Product
#     hero_data = to_update_product_data.model_dump(exclude_unset=True)
#     product.sqlmodel_update(hero_data)
#     session.add(product)
#     session.commit()
#     return product
