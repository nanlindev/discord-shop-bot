import logging
from discord import Client, User
from config import ADMIN_ID
from loguru import logger

async def notify_admin(title: str, content: str):
    try:
        from bot import app
        # Safely retrieve the Discord client instance from the application state
        client = getattr(app.state, 'discord_client', None)
        if not client:
            logger.warning('discord_client not found in App State, skipping notification')
            return
        
        user: User = await client.fetch_user(ADMIN_ID)
        if user:
            # Format the message using Markdown for better readability in Discord DMs
            message = f"### {title}\n\n{content}"
            await user.send(message)
            logger.info(f"Admin notification sent: {title}")
            
    except Exception as e:
        logger.error(f"Failed to send admin notification: {e}")