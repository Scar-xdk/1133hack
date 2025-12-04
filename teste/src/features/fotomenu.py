from telegram import Update
from telegram.ext import ContextTypes

from src.core.bot_manager import bot_manager


async def fotomenu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_manager.is_admin(update.effective_user.id):
        return
    
    await update.message.reply_text("📸 Por favor, envie a nova foto do menu:")
    context.user_data['waiting_photo'] = True


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_photo'):
        if not bot_manager.is_admin(update.effective_user.id):
            return
        
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive(bot_manager.menu_image)
        
        await update.message.reply_text("✅ Foto do menu atualizada com sucesso!")
        context.user_data['waiting_photo'] = False
