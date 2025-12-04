import json
from datetime import datetime
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.core.bot_manager import bot_manager


# ========== ADD GIFT ==========
async def add_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_manager.is_admin(update.effective_user.id):
        return
    
    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ Uso: /add_gift <nome> <valor>")

    gift_name = context.args[0]

    try:
        gift_value = float(context.args[1])
    except:
        return await update.message.reply_text("⚠️ O valor deve ser um número!")

    gifts = bot_manager.load_gifts()
    gifts[gift_name] = {
        "valor": gift_value,
        "criado_por": update.effective_user.id,
        "data_criacao": datetime.now().strftime("%Y-%m-%d"),
        "resgatado": False,
        "resgatado_por": None,
        "data_resgate": None
    }

    bot_manager.save_gifts(gifts)

    await update.message.reply_text(
        f"✅ Gift '{gift_name}' criado com valor R${gift_value:.2f}!"
    )


# ========== RESGATAR GIFT ==========
async def resgatar_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        return await update.message.reply_text("⚠️ Uso: /resgatar_gift <nome>")

    gift_name = context.args[0]
    gifts = bot_manager.load_gifts()

    if gift_name not in gifts:
        return await update.message.reply_text("⚠️ Esse gift não existe.")

    gift = gifts[gift_name]

    if gift["resgatado"]:
        return await update.message.reply_text("❌ Esse gift já foi resgatado.")

    # Atualiza gift
    gift.update({
        "resgatado": True,
        "resgatado_por": update.effective_user.id,
        "data_resgate": datetime.now().strftime("%Y-%m-%d")
    })

    bot_manager.save_gifts(gifts)

    # Atualiza usuário
    users = bot_manager.load_users()
    uid = str(update.effective_user.id)

    users[uid]["saldo"] += gift["valor"]
    users[uid]["gifts_resgatados"] += gift["valor"]

    bot_manager.save_users(users)

    await update.message.reply_text(
        f"🎉 Parabéns! Você resgatou o gift {gift_name}.\n"
        f"Seu saldo agora é R${users[uid]['saldo']:.2f} 💰"
    )


# ========== DELETAR GIFT ==========
async def del_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_manager.is_admin(update.effective_user.id):
        return
    
    if len(context.args) < 1:
        return await update.message.reply_text("⚠️ Uso: /del_gift <nome>")

    gift_name = context.args[0]
    gifts = bot_manager.load_gifts()

    if gift_name in gifts:
        del gifts[gift_name]
        bot_manager.save_gifts(gifts)
        await update.message.reply_text(f"✅ Gift '{gift_name}' deletado!")
    else:
        await update.message.reply_text("⚠️ Esse gift não existe.")


# ========== INFO GIFTS ==========
async def infogifts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_manager.is_admin(update.effective_user.id):
        return

    gifts = bot_manager.load_gifts()

    if not gifts:
        return await update.message.reply_text("📋 Nenhum gift cadastrado.")

    gifts_json = json.dumps(gifts, indent=2, ensure_ascii=False)

    await update.message.reply_text(
        f"📋 GIFTS:\n```json\n{gifts_json}\n```",
        parse_mode=ParseMode.MARKDOWN
    )
