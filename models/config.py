from config import DATABASE_URL

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["models.user", "models.product", "models.card", "models.order", "models.setting", "aerich.models"],
            "default_connection": "default",
        },
    },
    "log_level":"DEBUG",
}