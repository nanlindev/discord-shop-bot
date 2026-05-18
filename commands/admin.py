import discord
from discord import app_commands
from utils.logger_config import logger
from utils.role import is_owner
from utils.i18n import _ 

from services.stat_service import StatService
from models.product import Product
from components.dashboard_card import create_dashboard_display
from components.report_card import create_order_preview_embed, create_order_report_view, generate_order_csv, generate_product_csv

@app_commands.command(name="admin_stats", description=_("View system core data dashboard"))
@is_owner()
async def admin_stats(interaction: discord.Interaction):
    stats = await StatService.get_dashboard_stats()
    embed = create_dashboard_display(stats)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@app_commands.command(name="report", description=_("Generate today's order report"))
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
                await interaction.response.send_message(_("📤 Sending files..."), ephemeral=True)
                await interaction.followup.send(files=[order_csv_file, product_csv_file], ephemeral=True)
            else:
                await interaction.response.send_message(_("❌ Files have expired or were not found. Please regenerate the report."), ephemeral=True)
            
        view = create_order_report_view()
        for child in view.children:
            if isinstance(child, discord.ui.Button):
                child.callback = export_button_callback

        # 6. Send preview card + button
        await interaction.followup.send(
            embed=preview_embed,
            view=view,
            ephemeral=True # Keep admin only visible
        )

    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        await interaction.followup.send(_("❌ An error occurred while generating the report. Please check the backend logs."), ephemeral=True)

@app_commands.command(name='clear_chat', description=_('Clear a specified number of messages (Admin only)'))
@app_commands.describe(amount=_('Number of messages to delete (1-100)'))
@is_owner()
async def clear_chat(interaction: discord.Interaction, amount: int = 0):
    current_lang = str(interaction.locale).replace('-', '_')
    if amount > 100:
        await interaction.response.send_message(_("❌ You can only delete up to 100 messages at a time!", current_lang), ephemeral=True)
        return

    await interaction.response.send_message(_("🧹 Deleting the last {amount} messages...", current_lang).format(amount=amount), ephemeral=True)

    messages = [message async for message in interaction.channel.history(limit=amount)]
    try:
        deleted = await interaction.channel.delete_messages(messages) 
    except Exception as e:
        logger.exception(f'Deletion failed: {e}')
    logger.success(f"Successfully deleted {len(messages)} messages")

def register_admin_commands(tree: app_commands.CommandTree):
    tree.add_command(admin_stats)
    tree.add_command(clear_chat)
    tree.add_command(report)
    logger.info("✅ Admin commands registered")