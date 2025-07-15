# my_project/main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

# Change these relative imports to absolute imports
import crud
import models
import schemas
from database import engine, Base, get_db


# Create tables (if they don't exist) - typically done by dbt, but good for local testing
# Base.metadata.create_all(bind=engine) # Comment this out since dbt manages schemas

app = FastAPI(
    title="Telegram Medical Data Analytical API",
    description="API to query analytical insights from Telegram message and image detection data.",
    version="0.1.0",
)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Telegram Medical Data Analytical API!"}


# Endpoint 1: GET /api/reports/top-products?limit=10
@app.get("/api/reports/top-products", response_model=List[schemas.TopProduct])
def get_top_products_endpoint(
    limit: int = Query(
        10, ge=1, le=100, description="Number of top products to return"
    ),
    db: Session = Depends(get_db),
):
    products = crud.get_top_products(db, limit=limit)
    if not products:
        raise HTTPException(status_code=404, detail="No products found.")
    return products


# Endpoint 2: GET /api/channels/{channel_name}/activity
@app.get(
    "/api/channels/{channel_name}/activity",
    response_model=List[schemas.ChannelActivity],
)
def get_channel_activity_endpoint(channel_name: str, db: Session = Depends(get_db)):
    activity = crud.get_channel_activity(db, channel_username=channel_name)
    if not activity:
        raise HTTPException(
            status_code=404,
            detail=f"No activity found for channel '{channel_name}'. Ensure the channel exists and has messages/detections.",
        )
    return activity


# Endpoint 3: GET /api/search/messages?query=paracetamol
@app.get("/api/search/messages", response_model=List[schemas.Message])
def search_messages_endpoint(
    query: str = Query(
        ..., min_length=2, description="Keyword to search in message text"
    ),
    limit: int = Query(
        100, ge=1, le=500, description="Maximum number of messages to return"
    ),
    db: Session = Depends(get_db),
):
    messages = crud.search_messages(db, query=query, limit=limit)
    if not messages:
        raise HTTPException(
            status_code=404, detail=f"No messages found matching '{query}'."
        )
    return messages
