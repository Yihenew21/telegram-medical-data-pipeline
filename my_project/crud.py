# my_project/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, Date, case
from typing import List, Optional
from datetime import date

# Changed to absolute imports, assuming 'models' and 'schemas' are directly importable
import models
import schemas


# --- CRUD for fct_image_detections ---
def get_top_products(db: Session, limit: int = 10):
    return (
        db.query(
            models.FctImageDetection.detected_object_class,
            func.count(models.FctImageDetection.yolo_detection_key).label(
                "detection_count"
            ),
        )
        .group_by(models.FctImageDetection.detected_object_class)
        .order_by(desc("detection_count"))
        .limit(limit)
        .all()
    )


# --- CRUD for fct_messages and dim_channels ---
def get_channel_activity(db: Session, channel_username: str):
    channel = (
        db.query(models.DimChannel)
        .filter(models.DimChannel.channel_username == channel_username)
        .first()
    )

    if not channel:
        return None

    return (
        db.query(
            func.to_char(
                models.FctMessage.message_timestamp_utc.cast(Date), "YYYY-MM-DD"
            ).label("activity_date"),
            func.count(models.FctMessage.message_id).label("message_count"),
            func.count(models.FctImageDetection.yolo_detection_key).label(
                "detection_count"
            ),
            func.sum(models.FctMessage.views_count).label("total_views"),
            func.sum(models.FctMessage.forwards_count).label("total_forwards"),
            func.sum(models.FctMessage.replies_count).label("total_replies"),
            func.sum(case((models.FctMessage.has_media == True, 1), else_=0)).label(
                "messages_with_media"
            ),
        )
        .join(
            models.DimChannel,
            models.FctMessage.channel_pk == models.DimChannel.channel_pk,
        )
        .outerjoin(
            models.FctImageDetection,
            models.FctMessage.message_id == models.FctImageDetection.message_id,
        )
        .filter(models.DimChannel.channel_username == channel_username)
        .group_by(
            func.to_char(
                models.FctMessage.message_timestamp_utc.cast(Date), "YYYY-MM-DD"
            )
        )
        .order_by(
            func.to_char(
                models.FctMessage.message_timestamp_utc.cast(Date), "YYYY-MM-DD"
            )
        )
        .all()
    )


def search_messages(db: Session, query: str, limit: int = 100):
    return (
        db.query(models.FctMessage)
        .filter(models.FctMessage.message_text.ilike(f"%{query}%"))
        .limit(limit)
        .all()
    )
