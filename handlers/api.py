# webhook
from fastapi import APIRouter, Request, HTTPException, FastAPI, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
from services.order_service import OrderService
import stripe
import config
from utils.notification import notify_admin
from errors import InnerHandledError
from utils.i18n import _

router = APIRouter()

stripe.api_key = config.STRIPE_API_KEY
endpoint_secret = config.STRIPE_WEBHOOK_SECRET

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("✅ FastAPI started successfully, ready to serve requests...")
    yield
    logger.info("🛑 Received stop signal, shutting down gracefully...")

app = FastAPI(lifespan=lifespan)

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
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        discord_user_id = session.metadata.discord_id
        logger.info(f"🔔 Payment success notification received! Order ID: {session['id']}")
        try:
            await OrderService.handle_payment_success(session, discord_client)
            return JSONResponse(status_code=200, content={"status": "success", "message": "Processed"})
        except Exception as e:
            logger.error(f'Order processing error: {str(e)}')
            
            if discord_user_id:
                try:
                    user_error_msg = _("⚠️ **Automatic delivery failed**\n\nReason: {reason}\n\nPlease contact an administrator for assistance!").format(reason=str(e))
                    user = await discord_client.fetch_user(discord_user_id)
                    await user.send(user_error_msg)
                    logger.info(f"✅ Notified user {discord_user_id} of payment exception")
                except Exception as notify_err:
                    logger.error(f"❌ Failed to send DM to user: {notify_err}")
            
            if not isinstance(e, InnerHandledError):
                admin_title = _("💥 Critical Webhook Processing Error")
                admin_content = _("Order {order_no} processing failed.\nError message: {error}").format(
                    order_no=session.metadata.order_no, 
                    error=str(e)
                )
                await notify_admin(admin_title, admin_content)
                
            return JSONResponse(
                status_code=200, 
                content={"status": "error", "message": str(e)}
            )
    # 处理其他事件类型...
    return JSONResponse(status_code=200, content={"status": "ignored"})