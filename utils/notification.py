import logging
from discord import Client, User
from config import ADMIN_ID
from loguru import logger

async def notify_admin( title: str, content: str):
    try:
        from bot import app
        client = getattr(app.state, 'discord_client', None)
        if not client:
            logger.warning('App State中没有找到discord_client,跳过通知')
            return
        
        user: User = await client.fetch_user(ADMIN_ID)
        if user:
            message = f"### {title}\n\n{content}"
            await user.send(message)
            logger.info(f"已发送管理员通知: {title}")
            
    except Exception as e:
        logger.error(f"发送管理员通知失败: {e}")