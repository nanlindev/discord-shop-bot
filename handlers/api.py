#webhook
from fastapi import APIRouter, Request, HTTPException, FastAPI, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
from services.order_service import OrderService
import stripe
import config
from utils.notification import notify_admin
from errors import InnerHandledError

router = APIRouter()

stripe.api_key = config.STRIPE_API_KEY
endpoint_secret = config.STRIPE_WEBHOOK_SECRET

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("✅ FastAPI 启动成功，准备接客...")
    yield
    logger.info("🛑 收到停止信号，正在优雅退出...")
app = FastAPI(lifespan = lifespan)

@router.post("/webhook")
async def stripe_webhook(request: Request):
    discord_client = request.app.state.discord_client
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        raise HTTPException(status_code = 400, detail = "Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code = 400, detail = "Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        discord_user_id = session.metadata.discord_id
        logger.info(f"🔔 收到支付成功通知！订单号: {session['id']}")
        try:
            await OrderService.handle_payment_success(session, discord_client)
            return JSONResponse(status_code = 200, content = {"status": "success", "message": "Processed"})
        except Exception as e:
            logger.error(f'订单处理出错{str(e)}')
            #用户私信
            if discord_user_id:
                try:
                    user_error_msg = f"⚠️ **自动发货失败**\n\n原因：{str(e)}\n\n请联系管理员处理！"
                    user = await discord_client.fetch_user(discord_user_id)
                    await user.send(user_error_msg)
                    logger.info(f"✅ 已通知用户 {discord_user_id} 支付异常")
                except Exception as notify_err:
                    logger.error(f"❌ 给用户发私信失败: {notify_err}")
            #管理员私信
            if not isinstance(e, InnerHandledError):
                await notify_admin(
                    "💥 Webhook 处理严重错误",
                    f"订单 {session.metadata.order_no} 处理失败。\n错误信息: {str(e)}"
                )
            return JSONResponse(
                status_code = 200, # ⚠️ 注意：这里通常返回 200，告诉 Stripe "我收到消息了，不用再发了"
                content = {"status": "error", "message": str(e)}
            )
    # 处理其他事件类型...
    return JSONResponse(status_code = 200, content = {"status": "ignored"})
