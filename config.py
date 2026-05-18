import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# ============================================
# 1. Credentials (Loaded from .env)
# ============================================
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
PROXY_URL = os.getenv('PROXY_URL', None)  # Proxy URL, leave empty if not needed
ROLE_GAMER_ID = os.getenv('ROLE_GAMER_ID')

# ============================================
# 2. Database Configuration
# ============================================
BASE_DIR = Path(__file__).resolve().parent
raw_db_url = os.getenv("DATABASE_URL")

# Handle SQLite path resolution to ensure correct relative paths
if raw_db_url and raw_db_url.startswith("sqlite://"):
    db_filename = raw_db_url.replace("sqlite://", "")
    DATABASE_URL = f"sqlite:///{BASE_DIR / db_filename}"
else:
    DATABASE_URL = raw_db_url

# ============================================
# 3. Stripe Payment Configuration
# ============================================
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')
STRIPE_API_VERSION = os.getenv('STRIPE_API_VERSION')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

# Validation: Ensure critical credentials are present
if not DISCORD_BOT_TOKEN:
    raise ValueError('Discord Bot Token not found. Please check your .env file.')

# ============================================
# 4. Application Runtime Settings
# ============================================

# Global Runtime Variables
SHOP_STATUS = False  # Set to True to enable the shop for users

# Payment Result Pages
# These URLs define where users are redirected after a Stripe session.
# Current URLs point to your GitHub Pages hosted status pages.
STRIPE_SUCCESS_URL = 'https://nanlindev.github.io/discord-shop-bot/pages/success.html'
STRIPE_CANCEL_URL = 'https://nanlindev.github.io/discord-shop-bot/pages/cancel.html'

# Internationalization (i18n) Settings
I18N_PATH = 'locales'      # Directory where language files are stored
DEFAULT_LANGUAGE = 'en-US' # Default language code

# Administrator Configuration
# TODO: Replace with your actual Discord User ID for testing/management
ADMIN_ID = None #Example: 123456789012345678

# Role Mapping
# Maps internal role names to Discord Role IDs.
# Note: These IDs correspond to the roles users will receive upon purchase.
ROLE_MAP = {
    'Regular Player': ROLE_GAMER_ID,  # TODO: Ensure ROLE_GAMER_ID is set in .env
}
