import stripe
import discord
from models.user import User
from models.product import Product
from models.order import Order
from components.payment_view import PaymentView
from services.user_service import UserService
from utils.logger_config import logger
from services.order_service import OrderService
from components.order_list_card import OrderListCard
from config import STRIPE_SUCCESS_URL, STRIPE_CANCEL_URL
from utils.i18n import _

class UserHandler:
    @staticmethod
    async def handle_user_login(discord_id: int, username: str):
        user, created = await User.get_or_create(
            discord_id=discord_id,
            defaults={'username': username}
        )
        if created:
            await UserService.handle_add_point(user, 10)
            return _("Welcome newcomer! Here are 10 points for you")
        else:
            await UserService.handle_add_point(user, 1)
            return _("Welcome back! Here is 1 point for you")
        
    @staticmethod
    async def handle_buy(interaction: discord.Interaction, user: User, product: Product):
        order = Order(user=user, product=product)
        await order.save()
        logger.info(f'Order({order.id}) created successfully')
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product.name, 
                        },
                        'unit_amount': int(product.price * 100), 
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'{STRIPE_SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}', 
                cancel_url=STRIPE_CANCEL_URL,
                metadata={
                    'order_id': str(order.id),
                    'order_no': str(order.order_no),
                    'product_id': str(product.id),
                    'user_id': str(user.id),
                    'discord_id': str(user.discord_id),
                }
            )

            view = PaymentView(url=session.url, price=product.price)
            
            success_template = _("✅ You selected **{product_name}**, please click the button below to complete the payment:")
            await interaction.followup.send(
                success_template.format(product_name=product.name), 
                view=view
            )

        except Exception as e:
            error_template = _("❌ Payment system error: {error}")
            await interaction.followup.send(error_template.format(error=str(e)))

    @staticmethod
    async def handle_check_orders(interaction: discord.Interaction):
        """Handle order query request"""
        discord_id = interaction.user.id

        orders = await OrderService.get_user_orders(discord_id)

        embed = OrderListCard.create_order_list_display(orders)

        await interaction.response.send_message(embed=embed, ephemeral=True)