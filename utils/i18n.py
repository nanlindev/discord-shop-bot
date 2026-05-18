import gettext
import threading
import os
import discord
from discord.app_commands import Translator, TranslationContext, locale_str
from config import DEFAULT_LANGUAGE
from loguru import logger
from typing import Optional

local_ctx = threading.local()

def set_language(lang: str):
    """在 on_interaction 中调用，设置当前线程语言"""
    local_ctx.lang = lang

def _(text: str, current_lang: str = "") -> str:
    lang = current_lang or getattr(local_ctx, 'lang', DEFAULT_LANGUAGE)
    locale_file = lang.replace('-', '_')
    try:
        t = gettext.translation('messages', localedir='locales', languages=[locale_file])
    except FileNotFoundError:
        t = gettext.translation('messages', localedir='locales', languages=[DEFAULT_LANGUAGE], fallback=True)
    return t.gettext(text)


class DiscordCommandTranslator(Translator):
    def __init__(self):
        super().__init__()
        self._translations_cache = {}
        self._load_all_translations()

    def _load_all_translations(self):
        locales_dir = 'locales'
        if not os.path.exists(locales_dir):
            return
            
        for lang_dir in os.listdir(locales_dir):
            path = os.path.join(locales_dir, lang_dir, 'LC_MESSAGES', 'messages.mo')
            if os.path.exists(path):
                trans = gettext.translation('messages', localedir=locales_dir, languages=[lang_dir])
                self._translations_cache[lang_dir.replace('_', '-')] = trans

    def _get_translation(self, locale_str: str, message: str) -> str:
        trans = self._translations_cache.get(locale_str)
        if trans:
            return trans.gettext(message)
        
        lang_part = locale_str.split('_')[0]
        for key, trans in self._translations_cache.items():
            if key.startswith(lang_part):
                return trans.gettext(message)
                
        return message

    async def translate(
        self,
        string: locale_str,
        locale: discord.Locale,
        context: TranslationContext,
    ) -> str | None:
        locale_map = {
            discord.Locale.chinese: 'zh_CN',
            discord.Locale.american_english: 'en_US',
        }
        
        target_lang = locale_map.get(locale)
        
        if not target_lang:
            return None  
            
        translated = self._get_translation(target_lang, string.message)
        
        return translated

command_translator = DiscordCommandTranslator()