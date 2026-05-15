import discord
import config
import time
from discord import app_commands
from typing import List
from utils.setting import shop_open
from handlers.user_handler import UserHandler
from models.product import Product
from models.user import User
from errors import SpamDetectedError

user_cooldown_cache = {}

@app_commands.command(name = 'buy', description = '购买商品(卡密)')
@shop_open()
async def buy(interaction : discord.Interaction, product_id : str):
    #3秒防刷
    user_id = interaction.user.id
    current_time = time.time()
    cooldown_time = 3.0
    last_time = user_cooldown_cache.get(user_id, 0)
    if current_time - last_time < cooldown_time:
        raise SpamDetectedError(round(cooldown_time - (current_time - last_time), 1))
    user_cooldown_cache[user_id] = current_time

    try:
        pid = int(product_id)
    except ValueError:
        await interaction.response.send_message("❌ 找不到该商品", ephemeral = True)
        return
    product = await Product.get_or_none(id = pid, status = 'normal')
    if not product:
        # 3. 如果数据库里查不到这个ID，说明用户瞎蒙的或商品不存在
        await interaction.response.send_message("❌ 找不到该商品", ephemeral = True)
        return
    await interaction.response.defer(ephemeral = True)

    try:
        user = await User.get_or_none(discord_id = interaction.user.id)
        if not user:
            await interaction.followup.send('❌ 检测到您尚未登录,请先试用/login登录')
            return
        await UserHandler.handle_buy(interaction, user, product)
    except Exception as e:
        await interaction.followup.send(f'❌ 购买失败:{str(e)}')

@buy.autocomplete('product_id')
async def product_id_auticomplete(i : discord.Interaction, current : str) -> List[app_commands.Choice[str]]:
    if not config.SHOP_STATUS:
        return []

    if not current:
        products = await Product.filter(status = 'normal').order_by('-id').limit(25)
        choices = [app_commands.Choice(name = p.name, value = str(p.id)) for p in products]
    else:
        all_matched_products = await Product.filter(status = 'normal', name__icontains = current)
        sorted_products = sorted(all_matched_products, key = lambda p : (not p.name.lower().startswith(current.lower()), p.id))
        choices = [app_commands.Choice(name = p.name, value = str(p.id)) for p in sorted_products[:25]]
    return choices

def register_shop_commands(tree : app_commands.CommandTree):
    tree.add_command(buy)