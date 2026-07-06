from fastapi import HTTPException

from app.models.notification import Notification
from app.models.notification import NotificationType

def create_notification(
    db,
    user_id: int,
    message: str,
    type: NotificationType,
    reference_id: int | None = None
):
    new_notification = Notification(
        user_id=user_id,
        message=message,
        type=type.value,
        reference_id=reference_id
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification

def get_notifications(
    db,
    user_id: int,
    unread_only: bool = False
):
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.order_by(
        Notification.created_at.desc(),
        Notification.id.desc()
    ).all()

def mark_notification_as_read(
    db,
    notification_id: int,
    user_id: int
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .filter(Notification.user_id == user_id)
        .first()
    )
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification

def get_user_notifications(
    db,
    user_id: int,
    unread_only: bool = False
):
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.order_by(
        Notification.created_at.desc(),
        Notification.id.desc()
    ).all()