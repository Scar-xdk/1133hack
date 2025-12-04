import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.core.bot_manager import bot_manager

# ======== MOSTRAR PAISES ========

async def mostrar_paises(update: Update, context: ContextTypes.DEFAULT_TYPE, pagina=0):
    country = json.load(open("src/utils/country.json", "r", encoding="utf-8"))
    user = update.effective_user
    pais_atual = bot_manager.get_or_create_user(user).get("pais_atual")

    lista = list(country.keys())
    por_pag = 70
    ini, fim = pagina * por_pag, pagina * por_pag + por_pag

    botoes = []
    for i in range(ini, min(fim, len(lista)), 2):
        linha = []
        for j in (0, 1):
            if i + j < len(lista):
                p = lista[i + j]
                nome = country[p]["nome"] + (" (selecionado)" if pais_atual == p else "")
                linha.append(InlineKeyboardButton(nome, callback_data=f"pais_{p}"))
        botoes.append(linha)

    nav = []
    if pagina > 0:
        nav.append(InlineKeyboardButton("🔙 Anterior", callback_data=f"paises_{pagina-1}"))
    if fim < len(lista):
        nav.append(InlineKeyboardButton("🔜 Próxima", callback_data=f"paises_{pagina+1}"))
    if nav:
        botoes.append(nav)

    botoes.append([InlineKeyboardButton("🔙 Voltar Menu", callback_data="voltar_menu")])

    total = (len(lista) + por_pag - 1) // por_pag
    texto = f"🌍 Escolha seu país (página {pagina+1}/{total}):"
    rm = InlineKeyboardMarkup(botoes)

    if update.callback_query:
        await update.callback_query.message.edit_text(texto, reply_markup=rm)
    else:
        await update.message.reply_text(texto, reply_markup=rm)


# ======== SELECIONAR PAIS ========

async def selecionar_pais(update: Update, context: ContextTypes.DEFAULT_TYPE, pais_id):
    country = json.load(open("src/utils/country.json", "r", encoding="utf-8"))
    if pais_id not in country:
        return await update.callback_query.answer("País inválido.")

    user = update.effective_user
    users = bot_manager.load_users()
    uid = str(user.id)

    if uid not in users:
        bot_manager.get_or_create_user(user)
        users = bot_manager.load_users()

    users[uid].update({
        "pais": country[pais_id],
        "pais_id": pais_id,
        "pais_atual": pais_id
    })
    bot_manager.save_users(users)

    await update.callback_query.answer(
        f"✅ {country[pais_id]['nome']} selecionado!"
    )
    
    await mostrar_paises(update, context)
