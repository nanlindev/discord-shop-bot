import discord
from models.order import Order
from utils.i18n import _

class OrderListCard:
    @staticmethod
    def create_order_list_display(orders: list[Order]) -> discord.Embed:
        """Generate order list Embed"""
        if not orders:
            embed = discord.Embed(
                title=_("📦 My Orders"),
                description=_("You don't have any order records yet. Go check out the store!"),
                color=discord.Color.greyple()
            )
            return embed

        embed = discord.Embed(
            title=_("📦 My Order History"),
            color=discord.Color.blue()
        )

        for order in orders:
            status_label = order.get_status_label()
            product_name = order.product.name if order.product else _("Unknown Product")
            
            time_str = order.created_at.strftime("%Y-%m-%d %H:%M")
            
            field_name = _("🆔 Order No: `{order_no}`").format(order_no=order.order_no)
            
            field_value_template = _("{product_name} - **{amount}** - {time} - {status}")
            field_value = field_value_template.format(
                product_name=product_name, 
                amount=order.total_amount, 
                time=time_str, 
                status=status_label
            )
            
            embed.add_field(
                name=field_name,
                value=field_value,
                inline=False 
            )

        embed.set_footer(text=_("Showing only the last 10 orders"))
        return embed