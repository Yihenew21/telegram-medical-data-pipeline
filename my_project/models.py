# my_project/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    BigInteger,
    Date,
    Text,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

# Changed to absolute import, assuming 'database.py' is directly importable (e.g., in PYTHONPATH)
from database import Base


# Model for dim_channels (mapped from public_analytics.dim_channels)
class DimChannel(Base):
    __tablename__ = "dim_channels"
    __table_args__ = {"schema": "public_analytics"}

    channel_pk = Column(Text, primary_key=True, index=True)
    channel_username = Column(String(255), unique=True, index=True)

    messages = relationship("FctMessage", back_populates="channel")


# Model for fct_messages (mapped from public_analytics.fct_messages)
class FctMessage(Base):
    __tablename__ = "fct_messages"
    __table_args__ = {"schema": "public_analytics"}

    message_id = Column(BigInteger, primary_key=True, index=True)
    channel_pk = Column(Text, ForeignKey("public_analytics.dim_channels.channel_pk"))

    message_text = Column(Text)
    message_timestamp_utc = Column(Text)
    has_media = Column(Boolean)

    views_count = Column(Integer)
    forwards_count = Column(Integer)
    replies_count = Column(Integer)
    media_type = Column(Text)
    media_file_name = Column(Text)
    media_mime_type = Column(Text)
    media_file_size = Column(BigInteger)
    is_photo = Column(Boolean)
    is_document = Column(Boolean)
    date_pk = Column(Date)

    channel = relationship("DimChannel", back_populates="messages")
    detections = relationship("FctImageDetection", back_populates="message")


# Model for fct_image_detections (mapped from public_analytics.fct_image_detections)
class FctImageDetection(Base):
    __tablename__ = "fct_image_detections"
    __table_args__ = {"schema": "public_analytics"}

    yolo_detection_key = Column(Text, primary_key=True, index=True)
    message_id = Column(
        BigInteger, ForeignKey("public_analytics.fct_messages.message_id")
    )
    detected_object_class = Column(String)
    confidence_score = Column(Float)
    detection_timestamp = Column(DateTime)
    box_top_left_x = Column(Float)
    box_top_left_y = Column(Float)
    box_width = Column(Float)
    box_height = Column(Float)

    message = relationship("FctMessage", back_populates="detections")
