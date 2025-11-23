import os
import logging
import hmac
import hashlib
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфігурація (заповниш на Railway)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
WAYFORPAY_SECRET_KEY = os.environ.get('WAYFORPAY_SECRET_KEY', 'YOUR_WAYFORPAY_SECRET_KEY')
CHANNEL_ID = -1003479515000  # Твій канал
COURSE_PRICE = 290  # гривень

# ID повідомлень з відео в каналі (заповниш після завантаження)
VIDEO_MESSAGE_IDS = {
    'intro': 0,  # ID повідомлення з вступним відео
    'lesson1_video1': 0,  # ID повідомлення
    'lesson1_video2': 0,  # ID повідомлення
    'lesson2': 0,
    'lesson3': 0,
    'lesson4': 0,
    'lesson5': 0,
    'final': 0
}

# Flask додаток для webhook
app = Flask(__name__)
bot_app = None

# Функція для перевірки підпису Wayforpay
def verify_wayforpay_signature(data, signature):
    """Перевіряє підпис від Wayforpay"""
    fields_to_sign = [
        data.get('merchantAccount', ''),
        data.get('orderReference', ''),
        str(data.get('amount', '')),
        data.get('currency', ''),
        data.get('authCode', ''),
        data.get('cardPan', ''),
        data.get('transactionStatus', ''),
        data.get('reasonCode', '')
    ]
    
    sign_string = ';'.join(fields_to_sign)
    calculated_signature = hmac.new(
        WAYFORPAY_SECRET_KEY.encode('utf-8'),
        sign_string.encode('utf-8'),
        hashlib.md5
    ).hexdigest()
    
    return calculated_signature == signature

# Функція відправки всіх уроків
async def send_course_videos(chat_id: int):
    """Відправляє всі відео курсу користувачу"""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    try:
        # Вітальне повідомлення
        await bot.send_message(
            chat_id=chat_id,
            text="🎉 Вітаю! Дякую за покупку курсу по самомасажу!\n\n"
                 "Зараз ти отримаєш всі 7 відео уроків. Приємного навчання! 💆‍♀️"
        )
        
        # Вступне відео
        await bot.send_message(chat_id=chat_id, text="📹 Вступне відео:")
        await bot.forward_message(
            chat_id=chat_id,
            from_chat_id=CHANNEL_ID,
            message_id=VIDEO_MESSAGE_IDS['intro'],
            protect_content=True
        )
        
        # Урок 1: Ноги (2 відео)
        await bot.send_message(chat_id=chat_id, text="📹 Урок 1: Ноги")
        await bot.forward_message(
            chat_id=chat_id,
            from_chat_id=CHANNEL_ID,
            message_id=VIDEO_MESSAGE_IDS['lesson1_video1'],
            protect_content=True
        )
        await bot.forward_message(
            chat_id=chat_id,
            from_chat_id=CHANNEL_ID,
            message_id=VIDEO_MESSAGE_IDS['lesson1_video2'],
            protect_content=True
        )
        
        # Урок 2: Сідниці
        await bot.send_message(chat_id=chat_id, text="📹 Урок 2: Сідниці")
        await bot.forward_message(
            chat_id=chat_id,
            from_chat_id=CHANNEL_ID,
            message_id=VIDEO_MESSAGE_IDS['lesson2'],
            protect_content=True
        )
        
        # Урок 3: Спина
        await bot.send_message(chat_id=chat_id, text="📹 Урок 3: Спина")
        await bot.forward_message(
            chat_id=chat_id,
            from_chat_id=CHANNEL_ID,
            message_id=VIDEO_MESSAGE_IDS['lesson3'],
            protect_content=True
        )
        
        # Урок 4: Шия та Голова
        await bot.send_message(chat_id=chat_id, text="📹 Урок 4: Шия та Голова")
        await bot.forward_message(
            chat_id=chat_id,
            from_chat_id=CHANNEL_ID,
            message_id=VIDEO_MESSAGE_IDS['lesson4'],
            protect_content=True
        )
        
        # Урок 5: Руки
        await bot.send_message(chat_id=chat_id, text="📹 Урок 5: Руки")
        await bot.forward_message(
            chat_id=chat_id,
            from_chat_id=CHANNEL_ID,
            message_id=VIDEO_MESSAGE_IDS['lesson5'],
            protect_content=True
        )
        
        # Фінальне відео
        await bot.send_message(chat_id=chat_id, text="📹 Фінальне відео:")
        await bot.forward_message(
            chat_id=chat_id,
            from_chat_id=CHANNEL_ID,
            message_id=VIDEO_MESSAGE_IDS['final'],
            protect_content=True
        )
        
        # Заключне повідомлення
        await bot.send_message(
            chat_id=chat_id,
            text="✅ Це всі уроки курсу!\n\n"
                 "Практикуй регулярно для найкращих результатів. "
                 "Якщо є питання - пиши! 💪"
        )
        
        logger.info(f"Успішно відправлено курс користувачу {chat_id}")
        return True
        
    except Exception as e:
        logger.error(f"Помилка при відправці відео користувачу {chat_id}: {e}")
        return False

# Webhook від Wayforpay
@app.route('/webhook/payment', methods=['POST'])
async def payment_webhook():
    """Обробляє webhook від Wayforpay"""
    try:
        data = request.json
        logger.info(f"Отримано webhook: {data}")
        
        # Перевірка підпису
        signature = data.get('merchantSignature', '')
        if not verify_wayforpay_signature(data, signature):
            logger.warning("Невірний підпис Wayforpay!")
            return jsonify({'error': 'Invalid signature'}), 403
        
        # Перевірка статусу платежу
        if data.get('transactionStatus') == 'Approved':
            # Отримуємо chat_id з orderReference (формат: "order_CHATID_timestamp")
            order_ref = data.get('orderReference', '')
            try:
                chat_id = int(order_ref.split('_')[1])
                
                # Відправляємо курс
                success = await send_course_videos(chat_id)
                
                if success:
                    # Відповідь Wayforpay про успішну обробку
                    response_data = {
                        'orderReference': order_ref,
                        'status': 'accept',
                        'time': data.get('time')
                    }
                    
                    # Підписуємо відповідь
                    sign_string = f"{order_ref};accept;{data.get('time')}"
                    response_signature = hmac.new(
                        WAYFORPAY_SECRET_KEY.encode('utf-8'),
                        sign_string.encode('utf-8'),
                        hashlib.md5
                    ).hexdigest()
                    
                    response_data['signature'] = response_signature
                    return jsonify(response_data), 200
                else:
                    return jsonify({'error': 'Failed to send videos'}), 500
                    
            except (IndexError, ValueError) as e:
                logger.error(f"Помилка парсингу orderReference: {e}")
                return jsonify({'error': 'Invalid orderReference'}), 400
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Помилка в payment_webhook: {e}")
        return jsonify({'error': str(e)}), 500

# Команда /start для бота
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє команду /start"""
    chat_id = update.effective_chat.id
    
    await update.message.reply_text(
        f"👋 Вітаю!\n\n"
        f"Це бот для курсу самомасажу.\n\n"
        f"Твій Telegram ID: `{chat_id}`\n\n"
        f"Щоб отримати доступ до курсу, перейди на наш сайт та оплати курс.",
        parse_mode='Markdown'
    )

# Команда для отримання message_id (допоміжна, тільки для адміна)
async def get_message_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Допоміжна команда для отримання message_id з каналу"""
    # Перевіряємо чи це forward з каналу
    if update.message.forward_from_chat and update.message.forward_from_chat.id == CHANNEL_ID:
        message_id = update.message.forward_from_message_id
        await update.message.reply_text(
            f"Message ID цього відео в каналі: `{message_id}`\n\n"
            f"Додай його в код у словник VIDEO_MESSAGE_IDS",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "Щоб отримати message_id:\n"
            "1. Зайди в свій канал\n"
            "2. Forward (перешли) повідомлення з відео мені в приват\n"
            "3. Я дам тобі його message_id"
        )

# Обробник для всіх forwarded повідомлень з каналу
async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє forwarded повідомлення для отримання message_id"""
    if update.message.forward_from_chat and update.message.forward_from_chat.id == CHANNEL_ID:
        message_id = update.message.forward_from_message_id
        
        # Визначаємо тип медіа
        media_type = "невідомий тип"
        if update.message.video:
            media_type = "відео"
        elif update.message.photo:
            media_type = "фото"
        elif update.message.document:
            media_type = "документ"
            
        await update.message.reply_text(
            f"✅ Message ID: `{message_id}`\n"
            f"Тип: {media_type}\n\n"
            f"Збережи це число для коду!",
            parse_mode='Markdown'
        )

# Головна функція
@app.route('/webhook/telegram', methods=['POST'])
async def telegram_webhook():
    """Обробляє webhook від Telegram"""
    try:
        update = Update.de_json(request.json, bot_app.bot)
        await bot_app.process_update(update)
        return jsonify({'ok': True}), 200
    except Exception as e:
        logger.error(f"Помилка в telegram_webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    """Головна сторінка для перевірки"""
    return "Бот працює! 🤖"

@app.route('/health')
def health():
    """Health check для Railway"""
    return jsonify({'status': 'ok'}), 200

# Ініціалізація при запуску
def init_bot():
    """Ініціалізує Telegram бота"""
    global bot_app
    
    bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Додаємо обробники команд
    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("getmessageid", get_message_id))
    
    # Обробник forwarded повідомлень
    bot_app.add_handler(MessageHandler(
        filters.FORWARDED & (filters.VIDEO | filters.PHOTO | filters.Document.ALL),
        handle_forwarded_message
    ))
    
    logger.info("Бот ініціалізовано!")

if __name__ == '__main__':
    init_bot()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
