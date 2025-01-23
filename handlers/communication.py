# handlers/communication.py

from fastapi import FastAPI, HTTPException
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import aiosmtplib
from email.message import EmailMessage
from core.agent_base import AgentRouter
import json
import os

app = FastAPI()
router = AgentRouter()

# Initialize Telegram bot
telegram_bot = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

async def handle_whatsapp_message(message_data: dict):
    """Handle incoming WhatsApp messages."""
    try:
        # Process message based on type
        if "tour_id" in message_data:
            response = await router.route_message({
                "type": "trip_planner",
                "tour_id": message_data["tour_id"],
                "customization_needs": message_data.get("customization", {})
            })
        elif "content_url" in message_data:
            response = await router.route_message({
                "type": "content_creator",
                "content_type": "youtube",
                "content_url": message_data["content_url"]
            })
        else:
            raise HTTPException(status_code=400, detail="Invalid message format")
            
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def handle_telegram_message(update: Update):
    """Handle incoming Telegram messages."""
    try:
        message_text = update.message.text
        
        # Parse message to determine type and content
        if message_text.startswith('/customizetrip'):
            # Extract tour ID and customization needs
            parts = message_text.split()
            if len(parts) < 2:
                await update.message.reply_text("Please provide tour ID")
                return
                
            tour_id = parts[1]
            customization = " ".join(parts[2:]) if len(parts) > 2 else ""
            
            response = await router.route_message({
                "type": "trip_planner",
                "tour_id": tour_id,
                "customization_needs": {"text": customization}
            })
            
        elif message_text.startswith('/createcontent'):
            # Extract content URL
            parts = message_text.split()
            if len(parts) < 2:
                await update.message.reply_text("Please provide content URL")
                return
                
            content_url = parts[1]
            
            response = await router.route_message({
                "type": "content_creator",
                "content_type": "youtube",
                "content_url": content_url
            })
            
        else:
            await update.message.reply_text("Unknown command")
            return
            
        await update.message.reply_text(json.dumps(response, indent=2))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# # API endpoints
# @app.post("/webhook/whatsapp")
# async def whatsapp_webhook(message_data: dict):
#     """Webhook for WhatsApp messages."""
#     return await handle_whatsapp_message(message_data)

# @app.post("/webhook/telegram")
# async def telegram_webhook(update: Update):
#     """Webhook for Telegram messages."""
#     await handle_telegram_message(update, None)
#     return {"status": "ok"}

# Set up Telegram handlers
telegram_bot.add_handler(CommandHandler("start", handle_telegram_message))
telegram_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_telegram_message))