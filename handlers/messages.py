#测试回复
async def handle_message(message):
    if message.author.bot:
        return
    if '你好' in message.content:
        await message.channel.send('你好我是你的机器人')