import os
import io
import math
import json
import base64
import psutil
import asyncio
import logging
import aiohttp
from datetime import datetime
from PIL import Image
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from src.api.ApiGet5sim import buscar_servicos_por_pais
from src.features.paises import mostrar_paises, selecionar_pais
from src.core.bot_manager import bot_manager
from src.features.fotomenu import fotomenu, handle_photo
from src.features.gifts import add_gift, resgatar_gift, del_gift, infogifts
from src.features.broadcast import transmitir, handle_broadcast
from src.features.perfil import perfil

# ======= CONFIG LOG ======= 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
start_time = datetime.now()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = bot_manager.get_or_create_user(user)

    pais_info = user_data.get("pais", {})
    if isinstance(pais_info, dict):
        pais_nome = pais_info.get("nome", "🌎 Não selecionado")
    else:
        pais_nome = str(pais_info) if pais_info else "🌎 Não selecionado"

    user_id = user_data['id']
    user_link = f"<a href='tg://user?id={user_id}'>{user_id}</a>"

    welcome_text = f"""
💜 <b>Bem-vindo(a), {user_data['nome']}!</b>

🤖 Você está no <b>{bot_manager.config['nome']}</b> — a melhor plataforma para gerar números temporários e receber SMS de qualquer serviço, app ou site.

🏷️ <b>ID:</b> {user_link}
🌍 <b>País atual:</b> {pais_nome}
💰 <b>Saldo:</b> R$ {user_data['saldo']:.2f}

📘 Antes de continuar, leia nossos /termos.

🚀 Pronto pra começar? Explore o menu abaixo:
"""

    keyboard = [
        [
            InlineKeyboardButton("🌍 Países", callback_data="paises"),
            InlineKeyboardButton("🛠️ Services", callback_data="services")
        ],
        [InlineKeyboardButton("📢 Canal", url="https://t.me/SmsHunterFy")],
        [
            InlineKeyboardButton("💎 Recarregar", callback_data="recarregar"),
            InlineKeyboardButton("👤 Perfil", callback_data="perfil")
        ],
        [InlineKeyboardButton("🗑️ Apagar Menu", callback_data="apagar_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if os.path.exists(bot_manager.menu_image):
            with open(bot_manager.menu_image, 'rb') as photo:
                if update.callback_query:
                    try:
                        await update.callback_query.message.edit_caption(
                            caption=welcome_text,
                            reply_markup=reply_markup,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True
                        )
                    except:
                        await update.callback_query.message.delete()
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=photo,
                            caption=welcome_text,
                            reply_markup=reply_markup,
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True
                        )
                else:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=welcome_text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
        else:
            if update.callback_query:
                try:
                    await update.callback_query.message.edit_text(
                        welcome_text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                except:
                    await update.callback_query.message.delete()
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=welcome_text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
            else:
                await update.message.reply_text(
                    welcome_text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
    except Exception as e:
        logger.error(f"Erro no start: {e}")

# ======== TERMOS ========

async def termos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    termos_text = """
😃 <b>Para que serve esse bot?</b>
...
📲 <b>Nosso canal:</b> @SmsHunterfy
"""
    await update.message.reply_text(
        termos_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_manager.is_admin(update.effective_user.id): return

    users = bot_manager.load_users()
    data = json.dumps(users, indent=2, ensure_ascii=False)

    path = "data/users_export.json"
    with open(path, "w", encoding="utf-8") as f: f.write(data)

    with open(path, "rb") as f:
        await update.message.reply_document(
            document=f,
            filename=f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            caption=f"📋 Total de usuários: {len(users)}"
        )

async def comandos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    comandos_text = """📋 Comandos do ADM:
- /status
- /fotomenu
- /add_gift <nome> <valor>
- /del_gift <nome>
- /infogifts
- /users
- /transmitir

📋 Comandos gerais:
- /start
- /resgatar_gift <nome>"""
    
    await update.message.reply_text(comandos_text)
    
def buscar_servicos_por_pais(country):
    url = f"https://5sim.net/v1/guest/products/{country}/any"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        # JSON válido E é um dicionário
        if isinstance(data, dict):
            return data

        # Caso venha lista (raro)
        if isinstance(data, list):
            novo = {}
            for item in data:
                if isinstance(item, dict) and "name" in item:
                    nome = item["name"]
                    novo[nome] = item
            return novo

        return {}

    except Exception as e:
        print("ERRO JSON 5SIM:", e)
        return {}

async def mostrar_servicos(update: Update, context: ContextTypes.DEFAULT_TYPE, pagina: int = 0):
    query = update.callback_query
    user_id = str(update.effective_user.id)

    users = bot_manager.load_users()
    u = users.get(user_id)

    if not u or "pais_id" not in u:
        await query.message.reply_text("Selecione um país primeiro.")
        return

    country = u["pais_id"]

    # BUSCA REAL
    data = buscar_servicos_por_pais(country)

    if not isinstance(data, dict) or len(data) == 0:
        await query.message.edit_text("Nenhum serviço encontrado para este país.")
        return

    # FILTRAGEM
    services = []
    for name, info in data.items():
        if not isinstance(info, dict):
            continue

        qty = info.get("Qty") or info.get("qty")
        price = info.get("Price") or info.get("price")

        if price is None or qty is None:
            continue

        services.append({
            "name": name,
            "qty": qty,
            "price": price
        })

    if not services:
        await query.message.edit_text("Nenhum serviço disponível no momento.")
        return

    # PAGINAÇÃO
    per_page = 16
    total = len(services)
    start = pagina * per_page
    end = start + per_page

    page_services = services[start:end]

    keyboard = []
    row = []

    for idx, svc in enumerate(page_services):
        label = f"{svc['name']} | {svc['price']}₽"
        btn = InlineKeyboardButton(label, callback_data=f"servico_{svc['name']}")
        row.append(btn)

        if (idx + 1) % 4 == 0:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    # NAVEGAÇÃO
    nav = []
    if pagina > 0:
        nav.append(InlineKeyboardButton("⬅️ Anterior", callback_data=f"services_{pagina-1}"))
    if end < total:
        nav.append(InlineKeyboardButton("Próxima ➡️", callback_data=f"services_{pagina+1}"))

    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("Menu", callback_data="voltar_menu")])

    await query.message.edit_text(
        f"Serviços disponíveis — {country}\nPágina {pagina + 1}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "perfil":
        await perfil(update, context)
    elif data == "voltar_menu":
        await start(update, context)
    elif data == "apagar_menu":
        await query.answer("Menu apagado!")
        try:
            await query.message.delete()
        except:
            pass
    elif data == "paises":
        await mostrar_paises(update, context)
    elif data.startswith("pais_"):
        await selecionar_pais(update, context, data.split("_")[1])
    elif data == "paises_next":
        await paginar_paises(update, context, 1)
    elif data == "paises_back":
        await paginar_paises(update, context, -1)
    elif data == "services":
        await mostrar_servicos(update, context)
    elif data.startswith("servico_"):
        await selecionar_servico(update, context, data.split("_")[1])
    elif data.startswith("services_"):
        pagina = int(data.split("_")[1])
        await mostrar_servicos(update, context, pagina)
   
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_broadcast"):
        await handle_broadcast(update, context)
        
def main():
    application = Application.builder().token(bot_manager.config['token']).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("fotomenu", fotomenu))
    application.add_handler(CommandHandler("add_gift", add_gift))
    application.add_handler(CommandHandler("resgatar_gift", resgatar_gift))
    application.add_handler(CommandHandler("del_gift", del_gift))
    application.add_handler(CommandHandler("infogifts", infogifts))
    application.add_handler(CommandHandler("users", users_command))
    application.add_handler(CommandHandler("transmitir", transmitir))
    application.add_handler(CommandHandler("comandos", comandos))
    application.add_handler(CommandHandler("termos", termos))

    application.add_handler(
        CallbackQueryHandler(
            lambda u, c: mostrar_paises(u, c, int(u.callback_query.data.split('_')[1])),
            pattern=r"^paises_\d+$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            lambda u, c: mostrar_servicos(u, c, int(u.callback_query.data.split('_')[1])),
            pattern=r"^services_\d+$"
        )
    )

    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
