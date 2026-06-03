# Discord Shop Bot

A Discord bot designed to manage shop functionalities, user roles, and payments via Stripe. This bot allows server administrators to manage user tiers and handle payment processing directly through Discord.

github link: https://github.com/nanlindev/discord-shop-bot

---

## 🚀 Features

- **Shop Management:** Toggle shop availability globally.
- **Role Management:** Automatically assign Discord roles based on purchase tiers.
- **Payment Integration:** Integrated with Stripe for secure payment processing.
- **Multi-language Support:** Supports internationalization (i18n) for global users.
- **Proxy Support:** Optional proxy configuration for network restricted environments.

---

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/discord-shop-bot.git
cd discord-shop-bot
```

### 2. Install Dependencies

Make sure you have Python installed (3.8+ recommended).

```bash
pip install -r requirements.txt
```

### 3. Configuration

The bot requires two main configuration steps: setting up environment variables and configuring runtime settings.

### A. Environment Variables (.env)

Create a file named .env in the root directory and add your sensitive credentials:

```python
# Discord Bot Token (Required)
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Discord Role ID for "Gamer" (Required)
ROLE_GAMER_ID=your_role_id_here

# Database URL (Required)
# Example for SQLite: sqlite:///database.db
# Example for PostgreSQL: postgresql://user:password@localhost/dbname
DATABASE_URL=your_database_url_here

# Stripe API Keys (Required for payments)
STRIPE_API_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
STRIPE_API_VERSION=v1  # Optional

# Proxy Configuration (Optional)
# Leave empty if you have a direct connection
PROXY_URL=
```

### B. Runtime Configuration (config.py)

Open config.py to configure the bot's behavior. You must update the following variables:

ADMIN_ID: Important! Replace the default ID with your own Discord User ID to grant yourself administrator privileges for testing.

```python
ADMIN_ID = 123456789012345678  # Replace with your actual Discord User ID
```

ROLE_MAP: Map your in-game tiers to Discord Role IDs.

```python
ROLE_MAP = {
    'Regular Player': 'actual_role_id_here',
}
```

STRIPE_SUCCESS_URL & STRIPE_CANCEL_URL: Ensure these point to valid HTML pages hosted on your server or GitHub Pages to handle payment results correctly.

## Running with ngrok (Required for Stripe Webhooks)

Since Stripe needs to send payment callbacks to your local machine, you must expose your local server to the internet.

1. **Download ngrok:** Get it from ngrok.com.
2. **Start ngrok:** Run the following command in your terminal to forward port `8000` (or the port your bot uses):
3. **Copy the Forwarding URL:** ngrok will generate a public URL (e.g., `https://abcd-1234.ngrok-free.app`).
4. **Configure Stripe:**
   - Go to your Stripe Dashboard > Developers > Webhooks.
   - Add an endpoint using the ngrok URL followed by your webhook path (e.g., `https://abcd-1234.ngrok-free.app/webhook`).
   - Copy the **Signing Secret** (`whsec_...`) and paste it into your `.env` file as `STRIPE_WEBHOOK_SECRET`.

### 4. Running the Bot

Once configured, you can start the bot using:

```bash
python bot.py
```

### ⚙️ Key Configuration Details

### Database

The bot automatically detects if you are using SQLite and resolves the path relative to the project directory. If using PostgreSQL or MySQL, ensure the DATABASE_URL in your .env file is correct.

### Internationalization (i18n)

Path: Translations are stored in the locales folder.
Default Language: Set via DEFAULT_LANGUAGE in config.py (default is en-US).

### Proxy

If the bot cannot connect to Discord or Stripe due to network restrictions, set the PROXY_URL in your .env file (e.g., http://127.0.0.1:7890).

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### 📄 License

This project is licensed under the MIT License.
