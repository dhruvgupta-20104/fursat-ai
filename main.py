# main.py

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from telegram import Update, Bot
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import json
import os
from datetime import datetime

from agents.content_creator import ContentCreatorAgent
from agents.trip_planner import TripPlannerAgent
from core.agent_base import AgentRouter
from handlers.communication import handle_whatsapp_message, handle_telegram_message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s -    %(message)s',
    filename='logs/fursat_ai.log'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Fursat.fun AI Multi-Agent System",
    description="API for managing travel content and trip planning",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))

# Initialize agents
content_creator = ContentCreatorAgent()
trip_planner = TripPlannerAgent()

# Initialize router
router = AgentRouter()
router.register_agent("content_creator", content_creator)
router.register_agent("trip_planner", trip_planner)

# Request models
class ContentRequest(BaseModel):
    content_url: str
    platform: str
    schedule_time: Optional[datetime] = None

class TripRequest(BaseModel):
    tour_id: str
    customization_needs: Dict[str, Any]

# API endpoints
@app.post("/api/v1/content/create")
async def create_content(request: ContentRequest, background_tasks: BackgroundTasks):
    """
    Create and schedule content from various sources
    """
    try:
        message = {
            "type": "content_creator",
            "content_url": request.content_url,
            "platform": request.platform,
            "schedule_time": request.schedule_time
        }
        
        # Process content creation in background
        background_tasks.add_task(router.route_message, message)
        
        return {
            "status": "processing",
            "message": "Content creation initiated",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error in content creation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/trip/customize")
async def customize_trip(request: TripRequest):
    """
    Customize a trip package based on user requirements
    """
    try:
        message = {
            "type": "trip_planner",
            "tour_id": request.tour_id,
            "customization_needs": request.customization_needs
        }
        
        response = await router.route_message(message)
        return response
    except Exception as e:
        logger.error(f"Error in trip customization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(message_data: dict):
    """
    Handle incoming WhatsApp messages
    """
    try:
        return await handle_whatsapp_message(message_data, router)
    except Exception as e:
        logger.error(f"Error in WhatsApp webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request, response_model=None):
    """
    Handle incoming Telegram messages
    """
    try:
        body = await request.json()
        update = Update.de_json(body, bot=bot)
        return await handle_telegram_message(update, router)
    except Exception as e:
        logger.error(f"Error in Telegram webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)