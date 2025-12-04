from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.core.bot_manager import bot_manager


async def perfil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_data = bot_manager.get_or_create_user(user)
    bot_username = (await context.bot.get_me()).username
    
    link_afiliado = f"https://t.me/{bot_username}?start={user_data['id']}"
    
    perfil_text = f"""
👤 <b>PERFIL</b>:
<b>Nome:</b> <code>{user_data['nome']}</code>
<b>Username:</b> <code>@{user_data['username']}</code>
<b>ID:</b> <code>{user_data['id']}</code>

💰 <b>CARTEIRA</b>:
<b>ID carteira:</b> {user_data['id']}
<b>Seu saldo atual:</b> R${user_data['saldo']:.2f}

🛒 <b>COMPRAS</b>:
<b>Números comprados:</b> {user_data['numeros_comprados']}
<b>Recargas feitas:</b> R${user_data['recargas_feitas']:.2f}
<b>Gifts resgatados:</b> R${user_data['gifts_resgatados']:.2f}

👥 <b>AFILIADOS</b>:
<b>Saldo ganho:</b> R${user_data['saldo_afiliado']:.2f}
<b>Indicações:</b> {user_data['indicacoes']}

🔗 <b>Link de afiliado:</b>
<code>{link_afiliado}</code>
"""

    keyboard = [
        [InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.message.edit_text(
            perfil_text, 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.HTML
        )
    except:
        await query.message.edit_caption(
            caption=perfil_text, 
            reply_markup=reply_markup, 
            parse_mode=ParseMode.HTML
        )
