#用户行为
import stripe
import discord
from models.user import User
from models.product import Product
from models.order import Order
from models.user import User
from components.payment_view import PaymentView
from services.user_service import UserService
from utils.logger_config import logger
from services.order_service import OrderService
from components.order_list_card import OrderListCard
from config import STRIPE_SUCCESS_URL, STRIPE_CANCEL_URL

class UserHandler:
    @staticmethod
    async def handle_user_login(discord_id: int, username: str):
        user, created = await User.get_or_create(
            discord_id = discord_id,
            defaults   = {'username' : username}
        )
        if created:
            #新用户+10分
            await UserService.handle_add_point(user, 10)
            return '欢迎新人!送你10分'
        else:
            #老用户+1分
            await UserService.handle_add_point(user, 1)
            return '欢迎回来!送你1分'
        
    @staticmethod
    async def handle_buy(interaction : discord.Interaction, user : User, product : Product):
        order = Order(user = user, product = product)
        await order.save()
        logger.info(f'订单({order.id})创建成功')
        try:
            # 调用 Stripe 生成结账会话
            session = stripe.checkout.Session.create(
                payment_method_types = ['card'],
                line_items = [{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product.name,  # 直接用库里读出来的商品名
                        },
                        'unit_amount': int(product.price * 100), # 库里读出来的价格乘100转成分
                    },
                    'quantity': 1,
                }],
                mode = 'payment',
                success_url = f'{STRIPE_SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}', 
                cancel_url = STRIPE_CANCEL_URL,
                metadata = {
                    'order_id': str(order.id),
                    'order_no': str(order.order_no),
                    'product_id': str(product.id),
                    'user_id': str(user.id),
                    'discord_id': str(user.discord_id),
                }
            )

            # 创建带支付按钮的交互组件
            view = PaymentView(url = session.url, price = product.price)
            # 发送带有按钮的消息给用户
            await interaction.followup.send(f"✅ 你选择了 **{product.name}**，请点击下方按钮完成付款：", view = view)

        except Exception as e:
            await interaction.followup.send(f"❌ 支付系统出错了：{e}")

    @staticmethod
    async def handle_check_orders(interaction: discord.Interaction):
        """处理查询订单请求"""
        discord_id = interaction.user.id

        orders = await OrderService.get_user_orders(discord_id)

        # 3. 调用 Component 生成界面
        embed = OrderListCard.create_order_list_display(orders)

        # 4. 回复 (Ephemeral=True 表示仅用户可见，保护隐私)
        await interaction.response.send_message(embed = embed, ephemeral = True)