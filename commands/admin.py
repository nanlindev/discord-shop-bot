import discord
from discord import app_commands
from utils.logger_config import logger
from utils.role import is_owner
from services.stat_service import StatService
from models.product import Product
from components.dashboard_card import create_dashboard_display
from components.report_card import create_order_preview_embed, create_order_report_view, generate_order_csv, generate_product_csv

@app_commands.command(name = "admin_stats", description = "查看系统核心数据看板")
@is_owner()
async def admin_stats(interaction: discord.Interaction):
    stats = await StatService.get_dashboard_stats()
    embed = create_dashboard_display(stats)
    await interaction.response.send_message(embed = embed, ephemeral = True)

@app_commands.command(name="report", description="生成今日订单报表")
@is_owner()
async def report(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        orders, total_revenue = await StatService.get_order_report_package()
        preview_embed = create_order_preview_embed(orders, total_revenue)

        all_products = await Product.all().order_by('-created_at')
        order_csv_file = generate_order_csv(orders)
        product_csv_file = generate_product_csv(all_products)

        async def export_button_callback(interaction: discord.Interaction):
            if order_csv_file and product_csv_file:
                await interaction.response.send_message("📤 正在发送文件...", ephemeral = True)
                await interaction.followup.send(files = [order_csv_file, product_csv_file], ephemeral = True)
            else:
                await interaction.response.send_message("❌ 文件已过期或未找到，请重新生成报表。", ephemeral = True)
            
        view = create_order_report_view()
        for child in view.children:
            if isinstance(child,discord.ui.Button):
                child.callback = export_button_callback

        # 6. 发送预览卡片 + 按钮
        await interaction.followup.send(
            embed = preview_embed,
            view = view,
            ephemeral = True # 保持仅管理员可见
        )

    except Exception as e:
        logger.error(f"生成报表失败: {e}")
        await interaction.followup.send("❌ 生成报表时发生错误，请检查后台日志。", ephemeral = True)

@app_commands.command(name = 'clear_chat', description = '清空指定数量的消息(管理员专用)')
@app_commands.describe(amount = '要删除的消息数量(1-100)')
@is_owner()
async def clear_chat(interaction: discord.Interaction, amount: int = 0):
    if amount > 100:
        await interaction.response.send_message("❌ 一次最多只能删除 100 条消息！", ephemeral = True)
        return

    await interaction.response.send_message(f"🧹 正在删除最近 {amount} 条消息...", ephemeral = True)

    messages = [message async for message in interaction.channel.history(limit = amount)]
    try:
        deleted = await interaction.channel.delete_messages(messages) 
    except Exception as e:
        logger.exception(f'删除失败:{e}')
    logger.success(f"成功删除 {len(messages)} 条消息")

def register_admin_commands(tree: app_commands.CommandTree):
    tree.add_command(admin_stats)
    tree.add_command(clear_chat)
    tree.add_command(report)
    logger.info("✅ 管理员指令已注册")

