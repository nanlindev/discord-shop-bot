import discord
import csv
import io
import datetime as dt
from utils.i18n import _

def create_order_report_view() -> discord.ui.View:
    """Create a view containing an export button"""
    view = discord.ui.View(timeout=None)
    button = discord.ui.Button(label=_("💾 Export Full CSV"), style=discord.ButtonStyle.green)
    button.custom_id = 'export_csv_btn'
    view.add_item(button)
    return view

def create_order_preview_embed(orders, total_revenue: float) -> discord.Embed:
    embed = discord.Embed(title=_("📊 Today's Order Report Preview"), color=discord.Color.blue())
    embed.add_field(name=_("Total Revenue"), value=f"¥ {total_revenue}", inline=False)
    embed.add_field(name=_("Total Orders"), value=_("{count} orders").format(count=len(orders)), inline=True)
    
    description = ""
    for order in orders[:5]:
        status_emoji = "✅" if order.is_paid else "⏳"
        username = order.user.username if order.user else _("Unknown User")
        product_name = order.product.name if order.product else _("Deleted Product")
        description += _("{emoji} **{username}** - {product} - ¥{amount}\n").format(
            emoji=status_emoji, 
            username=username, 
            product=product_name, 
            amount=order.total_amount
        )
    
    if not description:
        description = _("No orders today.")
        
    embed.add_field(name=_("Latest Orders (Top 5)"), value=description, inline=False)
    embed.set_footer(text=_("Click the button below to export the full Excel/CSV file"))

    return embed

def generate_order_csv(orders) -> discord.File:
    """Generate CSV file object"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Order No", "User ID", "Username", "Product Name", "Amount", "Status", "Created At"])
    
    for order in orders:
        status_text = "Paid" if order.is_paid else "Pending"
        username = order.user.username if order.user else "Unknown"
        product_name = order.product.name if order.product else "Deleted"
        created_at = order.created_at.strftime("%Y-%m-%d %H:%M:%S")
        
        writer.writerow([
            order.order_no,
            order.discord_id,
            username,
            product_name,
            order.total_amount,
            status_text,
            created_at
        ])
    
    byte_output = io.BytesIO(output.getvalue().encode('utf-8-sig'))
    filename = f"orders_{dt.datetime.now().strftime('%Y%m%d')}.csv"
    return discord.File(byte_output, filename=filename)

def generate_product_csv(products) -> discord.File:
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Product Name", "Price", "Stock Quantity", "Status", "Created At"])

    for product in products:
        status_text = "Active" if getattr(product, 'normal', True) else "Inactive" 
        created_at = product.created_at.strftime("%Y-%m-%d %H:%M:%S") if product.created_at else "Unknown"

        writer.writerow([
            product.name,
            f"{product.price}", 
            product.stock,      
            status_text,
            created_at
        ])

    byte_output = io.BytesIO(output.getvalue().encode('utf-8-sig'))
    filename = f"products_{dt.datetime.now().strftime('%Y%m%d')}.csv"
    return discord.File(byte_output, filename=filename)