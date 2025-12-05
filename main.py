
import logging
import os
import json
import uuid
import threading
import time
from datetime import datetime, timedelta
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

BOT_TOKEN = "SEU_TOKEN_DO_TELEGRAM_AQUI"
ADMIN_ID = 6939434522
API_BASE_URL = "http://localhost:3000"
PAYMENT_AMOUNT = 10.00
PAYMENT_TIMEOUT_MINUTES = 20
USERS_FILE = "users.json"
PHOTOS_DIR = "photos"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def load_user_data():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_user_data(data):
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_user(user_id, username, first_name):
    users = load_user_data()
    user_id_str = str(user_id)
    if user_id_str not in users:
        users[user_id_str] = {
            "username": username,
            "first_name": first_name,
            "coins": 0,
            "free_uses": 0,
            "referral_link": f"https://t.me/{(updater.bot.get_me()).username}?start={user_id_str}",
            "referrals": 0,
            "payments": [],
            "codes": [],
            "first_start": True
        }
    return users[user_id_str], users

def notify_admin(update: Update, context: CallbackContext, message: str, photo_path=None):
    try:
        if photo_path:
            context.bot.send_photo(chat_id=ADMIN_ID, photo=open(photo_path, 'rb'), caption=message)
        else:
            context.bot.send_message(chat_id=ADMIN_ID, text=message)
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    user_data, users = get_user(user.id, user.username, user.first_name)
    
    is_new_user = user_data.get("first_start", True)

    if context.args and is_new_user:
        referrer_id = context.args[0]
        if str(referrer_id) != str(user.id):
            referrer_data = users.get(str(referrer_id))
            if referrer_data:
                referrer_data["coins"] = referrer_data.get("coins", 0) + 1
                referrer_data["referrals"] = referrer_data.get("referrals", 0) + 1
                try:
                    context.bot.send_message(
                        chat_id=referrer_id,
                        text="🎉 Você ganhou 1 moeda por indicar um novo usuário! Digite /perfil para ver seu saldo."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify referrer {referrer_id}: {e}")

    user_data["first_start"] = False
    save_user_data(users)

    if is_new_user:
        notify_admin(update, context, f"👤 Novo usuário: {user.first_name} (@{user.username}, ID: {user.id}) deu /start.")

    keyboard = [[InlineKeyboardButton("✨ Criar Nude com IA", callback_data='create_nude')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        f"Olá, {user.first_name}! 👋\n\n"
        "Envie uma foto e nossa Inteligência Artificial irá remover as roupas da pessoa na imagem.\n\n"
        "Clique no botão abaixo para começar!\n\n"
        "💰 **Ganhe moedas!**\n"
        "Indique novos usuários com seu link e ganhe moedas para usar o bot de graça. A cada 100 moedas, você pode revelar uma foto sem custo.\n"
        f"Seu link de indicação é: `https://t.me/{(updater.bot.get_me()).username}?start={user.id}`"
    )
    
    update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN_V2)

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'create_nude':
        query.edit_message_text(text="Ótimo! Agora, por favor, envie a foto que você deseja processar.")

def perfil(update: Update, context: CallbackContext):
    user = update.effective_user
    user_data, _ = get_user(user.id, user.username, user.first_name)
    
    message = (
        f"👤 **Seu Perfil**\n\n"
        f"**Nome:** {user_data['first_name']}\n"
        f"**Username:** @{user_data['username']}\n\n"
        f"**Moedas:** {user_data['coins']} 🪙\n"
        f"**Usos gratuitos restantes:** {user_data['free_uses']}\n\n"
        f"**Como ganhar moedas?**\n"
        "Você ganha 1 moeda para cada novo usuário que iniciar o bot através do seu link de indicação. Com 100 moedas, você pode processar uma imagem de graça!\n\n"
        "**Seu link de indicação:**\n"
        f"`{user_data['referral_link']}`"
    )
    update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)

def nua(update: Update, context: CallbackContext):
    user = update.effective_user
    user_data, users = get_user(user.id, user.username, user.first_name)
    
    code = str(uuid.uuid4())[:8]
    user_data["codes"].append(code)
    save_user_data(users)
    
    notify_admin(update, context, f"🔑 Usuário {user.first_name} (@{user.username}) gerou um novo código de uso: {code}")

    update.message.reply_text(f"Seu novo código de uso é: `{code}`\n\nUse o comando `/ai {code}` para processar uma imagem.", parse_mode=ParseMode.MARKDOWN)

def ai_command(update: Update, context: CallbackContext):
    user = update.effective_user
    user_data, users = get_user(user.id, user.username, user.first_name)

    if not context.args:
        update.message.reply_text("Uso incorreto. Por favor, use o comando no formato: `/ai <código>`")
        return

    code = context.args[0]
    if code in user_data.get("codes", []):
        user_data["codes"].remove(code)
        user_data["free_uses"] = user_data.get("free_uses", 0) + 1
        save_user_data(users)
        update.message.reply_text("Código validado! Você ganhou +1 uso gratuito. Envie uma foto para processar.")
    else:
        update.message.reply_text("Código inválido ou já utilizado.")
        
def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    notify_admin(update, context, f"💬 Mensagem de {user.first_name} (@{user.username}):

{update.message.text}")
    update.message.reply_text("Eu sou um bot e só consigo processar fotos. Por favor, envie uma imagem.")

def check_payment_status(context, user_id, payment_id, message_to_edit, photo_file_id):
    user = context.bot.get_chat(user_id)
    user_data, users = get_user(user_id, user.username, user.first_name)

    start_time = datetime.now()
    while datetime.now() - start_time < timedelta(minutes=PAYMENT_TIMEOUT_MINUTES):
        try:
            response = requests.get(f"{API_BASE_URL}/aguardar-pagamento/{payment_id}", timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    message_to_edit.edit_text("✅ Pagamento confirmado! Sua foto está sendo liberada...")
                    context.bot.send_photo(user_id, photo_file_id)
                    user_data["free_uses"] = user_data.get("free_uses", 0) + 2
                    save_user_data(users)
                    context.bot.send_message(user_id, "Você ganhou +2 usos gratuitos! Use o comando /nua para gerar um código e /ai <code> para usá-lo.")
                    return
                elif data.get("success") is False:
                    message_to_edit.edit_text("❌ Pagamento foi cancelado.")
                    return
        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking payment status: {e}")
        
        time.sleep(5)

    try:
        requests.get(f"{API_BASE_URL}/cancelar/{payment_id}")
        message_to_edit.edit_text("⏰ O tempo para pagamento expirou e a cobrança foi cancelada automaticamente.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error cancelling payment after timeout: {e}")

def handle_photo(update: Update, context: CallbackContext):
    user = update.effective_user
    user_data, users = get_user(user.id, user.username, user.first_name)

    if user_data.get("free_uses", 0) > 0:
        user_data["free_uses"] -= 1
        save_user_data(users)
        update.message.reply_text("Você usou um passe gratuito! Processando sua imagem...")
        time.sleep(3)
        context.bot.send_photo(user.id, update.message.photo[-1].file_id)
        update.message.reply_text(f"Processamento concluído! Você ainda tem {user_data['free_uses']} usos gratuitos.")
        return

    if user_data.get("coins", 0) >= 100:
        user_data["coins"] -= 100
        save_user_data(users)
        update.message.reply_text("Você usou 100 moedas! Processando sua imagem...")
        time.sleep(3)
        context.bot.send_photo(user.id, update.message.photo[-1].file_id)
        update.message.reply_text(f"Processamento concluído! Seu novo saldo é de {user_data['coins']} moedas.")
        return

    photo_file = update.message.photo[-1].get_file()
    photo_path = os.path.join(PHOTOS_DIR, f"{photo_file.file_id}.jpg")
    photo_file.download(photo_path)
    notify_admin(update, context, f"📸 Usuário {user.first_name} (@{user.username}) enviou uma foto para processamento.", photo_path=photo_path)

    progress_msg = update.message.reply_text("Tirando a roupa... 😈")
    time.sleep(5)
    
    try:
        payload = {"total_amount": PAYMENT_AMOUNT}
        response = requests.post(f"{API_BASE_URL}/criar-pagamento", json=payload)
        response.raise_for_status()
        payment_data = response.json()
        payment_id = payment_data["id"]
        pix_payload = payment_data["pix_payload"]
        
        user_data["payments"].append(payment_id)
        save_user_data(users)

        qr_url = f"{API_BASE_URL}/qr/{payment_id}"
        
        payment_message = (
            f"🔥 Sua foto está quase pronta! Para liberar o resultado completo, realize o pagamento de R$ {PAYMENT_AMOUNT:.2f} via PIX.\n\n"
            f"Você tem **{PAYMENT_TIMEOUT_MINUTES} minutos** para pagar, senão o pedido será cancelado.\n\n"
            f"Após o pagamento, sua foto será liberada instantaneamente e você ganhará **+2 usos gratuitos**!\n\n"
            f"👇 Copie o código Pix ou escaneie o QR Code:\n\n"
            f"`{pix_payload}`"
        )
        
        sent_message = context.bot.send_photo(
            chat_id=user.id,
            photo=qr_url,
            caption=payment_message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        threading.Thread(
            target=check_payment_status, 
            args=(context, user.id, payment_id, sent_message, update.message.photo[-1].file_id)
        ).start()

    except requests.exceptions.RequestException as e:
        logger.error(f"API payment creation failed: {e}")
        progress_msg.edit_text("Desculpe, não foi possível criar o pedido de pagamento no momento. Tente novamente mais tarde.")
    except (KeyError, TypeError):
        logger.error(f"Invalid API response: {response.text}")
        progress_msg.edit_text("Desculpe, ocorreu um erro inesperado com nosso sistema de pagamento. Tente novamente mais tarde.")

def main():
    global updater
    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)

    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("perfil", perfil))
    dispatcher.add_handler(CommandHandler("nua", nua))
    dispatcher.add_handler(CommandHandler("ai", ai_command))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    updater.start_polling()
    logger.info("Bot started polling.")
    updater.idle()

if __name__ == '__main__':
    main()
