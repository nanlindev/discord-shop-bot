from utils.i18n import _

async def handle_message(message):
    if message.author.bot:
        return
    
    if 'hello' in message.content.lower():
        await message.channel.send(_("Hello, I am your bot"))