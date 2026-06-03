import discord
from utils.i18n import _

# Define shop maintenance error
class ShopMaintenanceError(discord.app_commands.AppCommandError):
    def __init__(self):
        # User-facing message wrapped in _() for multi-language support
        super().__init__(_("🛑 The shop is currently under maintenance. Please try again later!"))

# Define insufficient permissions error
class MissingPermissionsError(discord.app_commands.AppCommandError):
    def __init__(self):
        # User-facing message wrapped in _() for multi-language support
        super().__init__(_("🚫 You do not have permission to execute this command!"))

# Cooldown / Spam detection
class SpamDetectedError(discord.app_commands.AppCommandError):
    def __init__(self, retry_after: float):
        # User-facing message with dynamic variable, wrapped in _()
        super().__init__(_("⚠️ Action too frequent! Please wait {retry_after:.1f} seconds before trying again.").format(retry_after=retry_after))

# Suspicious transaction / Economic anomaly
class SuspiciousTransactionError(discord.app_commands.AppCommandError):
    def __init__(self, reason: str):
        # User-facing message with dynamic variable, wrapped in _()
        super().__init__(_("⚠️ Transaction intercepted: {reason}").format(reason=reason))

# Internal marker exception, used to prevent duplicate alerts in the global error handler
class InnerHandledError(Exception):
    pass