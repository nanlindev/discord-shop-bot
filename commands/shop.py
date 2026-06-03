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
# 记得引入翻译函数
from utils.i18n import _ 

user_cooldown_cache = {}

@app_commands.command(name='buy', description=_("Purchase product (license key)"))
@shop_open()
async def buy(interaction: discord.Interaction, product_id: str):
    # 3-second anti-spam
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
        await interaction.response.send_message(_("❌ Product not found"), ephemeral=True)
        return
    
    product = await Product.get_or_none(id=pid, status='normal')
    if not product:
        # 3. If the ID is not found in the database, the user guessed wrong or the product does not exist
        await interaction.response.send_message(_("❌ Product not found"), ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)

    try:
        user = await User.get_or_none(discord_id=interaction.user.id)
        if not user:
            await interaction.followup.send(_('❌ You are not logged in. Please use /login first.'))
            return
        await UserHandler.handle_buy(interaction, user, product)
    except Exception as e:
        await interaction.followup.send(_('❌ Purchase failed: {error}').format(error=str(e)))

@buy.autocomplete('product_id')
async def product_id_autocomplete(i: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
    if not config.SHOP_STATUS:
        return []

    if not current:
        products = await Product.filter(status='normal', stock__gt=0).order_by('-id').limit(25)
        # 自动补全选项里的文案也要走翻译
        choices = [app_commands.Choice(name=_('[ID:{id}] {name} ({stock} left)').format(id=p.id, name=p.name, stock=p.stock), value=str(p.id)) for p in products]
    else:
        all_matched_products = await Product.filter(status='normal', name__icontains=current, stock__gt=0)
        sorted_products = sorted(all_matched_products, key=lambda p: (not p.name.lower().startswith(current.lower()), p.id))
        choices = [app_commands.Choice(name=_('[ID:{id}] {name} ({stock} left)').format(id=p.id, name=p.name, stock=p.stock), value=str(p.id)) for p in sorted_products[:25]]
    return choices

def register_shop_commands(tree: app_commands.CommandTree):
    tree.add_command(buy)