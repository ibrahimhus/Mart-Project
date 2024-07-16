from app.models.notification_model import Notification
from sqlmodel import Session, select  
from fastapi import HTTPException 

# Add a New notification to the Database
def add_new_notification(notification_data:Notification, session:Session):
    session.add(notification_data)
    session.commit()
    session.refresh(notification_data)
    return notification_data


# Get All inventory from the DB.
def get_all_notifications(session:Session):
    all_notifications = session.exec(select(Notification)).all()
    return all_notifications


# Get a notification by ID
def get_notification_by_id(notification_id:int, session:Session):
    notification = session.exec(select(Notification).where(Notification.id == notification_id)).one_or_none() 
    if notification is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return notification

# Delete Notification by ID
def delete_notification_by_id(notification_id:int, session:Session):
    notification = session.exec(select(Notification).where(Notification.id == notification_id)).one_or_none() 
    if notification is None:
        raise HTTPException(status_code=404, detail="Product not found")
    session.delete(notification)
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
