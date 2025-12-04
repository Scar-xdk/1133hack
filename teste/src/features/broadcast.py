import json
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.core.bot_manager import bot_manager

logger = logging.getLogger(__name__)


# =============== TRANSMITIR ===============
async def transmitir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_manager.is_admin(update.effective_user.id):
        return
    
    await update.message.reply_text(
        "📢 Digite a mensagem para transmitir.\n\n"
        "Use HTML:\n<b>negrito</b> <i>itálico</i> <code>código</code> <a href='url'>link</a>\n\n"
        "📌 Botões inline (opcional), use JSON:\n"
        "<b>Promoção!</b>\n```json\n[[{\"text\":\"🎁 Ver\",\"url\":\"https://t.me/SmsHunterFy\"}]]\n```\n\n"
        "Múltiplas linhas:\n```json\n[[{\"text\":\"1\",\"url\":\"https://1.com\"}],[{\"text\":\"2\",\"url\":\"https://2.com\"}]]```",
        parse_mode=ParseMode.HTML
    )
    
    context.user_data["waiting_broadcast"] = True



# =============== HANDLE BROADCAST ===============
async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_broadcast"):
        return
    
    if not bot_manager.is_admin(update.effective_user.id):
        return

    txt = update.message.text
    reply_markup = None

    try:
        # JSON com ```json
        if "```json" in txt:
            p = txt.split("```json")
            txt, js = p[0].strip(), p[1].split("```")[0].strip()
            data = json.loads(js)

        # JSON direto no texto
        elif "[[" in txt:
            i = txt.find("[[")
            data = json.loads(txt[i:])
            txt = txt[:i].strip()

        else:
            data = None

        # Monta botões
        if data:
            kb = [
                [InlineKeyboardButton(btn["text"], url=btn["url"]) for btn in row]
                for row in data
            ]
            reply_markup = InlineKeyboardMarkup(kb)

    except Exception as e:
        await update.message.reply_text(
            f"⚠️ Erro ao processar JSON: {e}\nEnviando sem botões..."
        )

    users = bot_manager.load_users()
    success, failed = 0, 0

    # Envio para todos os usuários
    for uid in users:
        try:
            await context.bot.send_message(
                int(uid),
                txt,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
            success += 1
            await asyncio.sleep(0.05)

        except Exception as e:
            logger.error(f"Erro ao enviar para {uid}: {e}")
            failed += 1

    await update.message.reply_text(
        f"✅ Concluído!\nEnviadas: {success}\nFalhas: {failed}"
    )
    
    context.user_data["waiting_broadcast"] = False
