# my_project/schemas.py
from pydantic import BaseModel
from datetime import datetime, date  # Import date for date_pk
from typing import Optional, List


# Schema for FctImageDetection API response
class ImageDetection(BaseModel):
    yolo_detection_key: str
    message_id: int
    detected_object_class: str
    confidence_score: float
    detection_timestamp: datetime
    box_top_left_x: Optional[float] = None
    box_top_left_y: Optional[float] = None
    box_width: Optional[float] = None
    box_height: Optional[float] = None

    class Config:
        from_attributes = True


# Schema for FctMessage API response (should match models.FctMessage and DB schema)
class Message(BaseModel):
    message_id: int
    # CORRECTED: channel_id -> channel_pk (matching DB and models.py)
    channel_pk: str  # Type is str as per your DB output (TEXT)

    message_text: Optional[str] = None

    # CORRECTED: message_timestamp -> message_timestamp_utc (matching DB and models.py)
    # Type is str as per your DB output (TEXT)
    message_timestamp_utc: Optional[str] = None

    # CORRECTED: has_media: Optional[int] -> has_media: Optional[bool] (matching DB and models.py)
    has_media: Optional[bool] = None

    # ADDED: Include all other fields from your fct_messages table based on \d output
    views_count: Optional[int] = None
    forwards_count: Optional[int] = None
    replies_count: Optional[int] = None
    media_type: Optional[str] = None
    media_file_name: Optional[str] = None
    media_mime_type: Optional[str] = None
    media_file_size: Optional[int] = None  # Or Optional[int] for bigint
    is_photo: Optional[bool] = None
    is_document: Optional[bool] = None
    date_pk: Optional[date] = None  # Type is date as per your DB output (DATE)

    class Config:
        from_attributes = True


# Schema for DimChannel API response (should match models.DimChannel and DB schema)
class Channel(BaseModel):
    # CORRECTED: channel_id -> channel_pk (matching DB and models.py)
    channel_pk: str  # Type is str as per your DB output (TEXT)
    channel_username: Optional[str] = None

    # REMOVED: channel_name - Not present in your \d public_analytics.dim_channels view output
    # If it is in the underlying table and you need it, ensure it's selected in dbt view.
    # channel_name: Optional[str] = None # Uncomment if it exists and you need it

    class Config:
        from_attributes = True


# Schema for top products report (remains the same)
class TopProduct(BaseModel):
    detected_object_class: str
    detection_count: int

    class Config:
        from_attributes = True


# Schema for channel activity report (remains the same)
class ChannelActivity(BaseModel):
    activity_date: str
    message_count: int
    detection_count: int
    # ADDED: Include other aggregated fields from crud.py get_channel_activity
    total_views: Optional[int] = None
    total_forwards: Optional[int] = None
    total_replies: Optional[int] = None
    messages_with_media: Optional[int] = None

    class Config:
        from_attributes = True
