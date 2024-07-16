from app.models.user_model import User
from sqlmodel import Session, select  
from fastapi import HTTPException 

# Add a New inventory to the Database
def add_new_user(user_data:User, session:Session):
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return user_data

# Get All users from the DB.
def get_all_users(session:Session):
    all_users = session.exec(select(User)).all()
    return all_users

# Get a user by ID
def get_user_by_id(user_id:int, session:Session):
    user = session.exec(select(User).where(User.id == user_id)).one_or_none() 
    if user is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return user

# Delete User by ID
def delete_user_by_id(user_id:int, session:Session):
    user = session.exec(select(User).where(User.id == user_id)).one_or_none() 
    if user is None:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(user)
    session.commit()
    return {'message': "User deleted successfully"}

# Update User by ID
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
