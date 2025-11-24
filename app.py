import os
import logging
import hmac
import hashlib
import asyncio
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Налаштування логування

logging.basicConfig(
format=’%(asctime)s - %(name)s - %(levelname)s - %(message)s’,
level=logging.INFO
)
logger = logging.getLogger(**name**)

# Конфігурація

TELEGRAM_BOT_TOKEN = os.environ.get(‘TELEGRAM_BOT_TOKEN’, ‘YOUR_BOT_TOKEN_HERE’)
WAYFORPAY_SECRET_KEY = os.environ.get(‘WAYFORPAY_SECRET_KEY’, ‘YOUR_WAYFORPAY_SECRET_KEY’)
CHANNEL_ID = -1003479515000
COURSE_PRICE = 290

# ID повідомлень з відео в каналі

VIDEO_MESSAGE_IDS = {
‘intro’: 0,
‘lesson1_video1’: 0,
‘lesson1_video2’: 0,
‘lesson2’: 0,
‘lesson3’: 0,
‘lesson4’: 0,
‘lesson5’: 0,
‘final’: 0
}

# Flask додаток

app = Flask(**name**)
bot_application = None

# Функція для перевірки підпису Wayforpay

def verify_wayforpay_signature(data, signature):
“”“Перевіряє підпис від Wayforpay”””
fields_to_sign = [
data.get(‘merchantAccount’, ‘’),
data.get(‘orderReference’, ‘’),
str(data.get(‘amount’, ‘’)),
data.get(‘currency’, ‘’),
data.get(‘authCode’, ‘’),
data.get(‘cardPan’, ‘’),
data.get(‘transactionStatus’, ‘’),
data.get(‘reasonCode’, ‘’)
]

```
sign_string = ';'.join(fields_to_sign)
calculated_signature = hmac.new(
    WAYFORPAY_SECRET_KEY.encode('utf-8'),
    sign_string.encode('utf-8'),
    hashlib.md5
).hexdigest()

return calculated_signature == signature
```

# Асинхронна функція відправки відео

async def send_course_videos_async(chat_id: int):
“”“Відправляє всі відео курсу користувачу”””
bot = Bot(token=TELEGRAM_BOT_TOKEN)

```
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
    
    # Урок 1: Ноги
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
```

# Синхронна обгортка

def send_course_videos(chat_id: int):
“”“Синхронна обгортка для відправки відео”””
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
return loop.run_until_complete(send_course_videos_async(chat_id))
finally:
loop.close()

# Webhook від Wayforpay

@app.route(’/webhook/payment’, methods=[‘POST’])
def payment_webhook():
“”“Обробляє webhook від Wayforpay”””
try:
data = request.json
logger.info(f”Отримано webhook: {data}”)

```
    # Перевірка підпису
    signature = data.get('merchantSignature', '')
    if not verify_wayforpay_signature(data, signature):
        logger.warning("Невірний підпис Wayforpay!")
        return jsonify({'error': 'Invalid signature'}), 403
    
    # Перевірка статусу платежу
    if data.get('transactionStatus') == 'Approved':
        order_ref = data.get('orderReference', '')
        try:
            chat_id = int(order_ref.split('_')[1])
            
            # Відправляємо курс
            success = send_course_videos(chat_id)
            
            if success:
                response_data = {
                    'orderReference': order_ref,
                    'status': 'accept',
                    'time': data.get('time')
                }
                
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
```

# Команди бота

async def start_command(update: Update, context):
“”“Обробляє команду /start”””
chat_id = update.effective_chat.id

```
await update.message.reply_text(
    f"👋 Вітаю!\n\n"
    f"Це бот для курсу самомасажу.\n\n"
    f"Твій Telegram ID: `{chat_id}`\n\n"
    f"Щоб отримати доступ до курсу, перейди на наш сайт та оплати курс.",
    parse_mode='Markdown'
)
```

async def handle_forwarded_message(update: Update, context):
“”“Обробляє forwarded повідомлення для отримання message_id”””
if update.message.forward_from_chat and update.message.forward_from_chat.id == CHANNEL_ID:
message_id = update.message.forward_from_message_id

```
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
```

# Telegram webhook

@app.route(’/webhook/telegram’, methods=[‘POST’])
def telegram_webhook():
“”“Обробляє webhook від Telegram”””
try:
if bot_application is None:
logger.error(“Bot application not initialized”)
return jsonify({‘error’: ‘Bot not ready’}), 503

```
    update = Update.de_json(request.json, bot_application.bot)
    
    # Запускаємо обробку в новому event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(bot_application.process_update(update))
    finally:
        loop.close()
        
    return jsonify({'ok': True}), 200
except Exception as e:
    logger.error(f"Помилка в telegram_webhook: {e}")
    return jsonify({'error': str(e)}), 500
```

@app.route(’/’)
def home():
“”“Головна сторінка”””
return “Бот працює! 🤖”

@app.route(’/health’)
def health():
“”“Health check”””
return jsonify({‘status’: ‘ok’}), 200

# Ініціалізація

def init_bot():
“”“Ініціалізує Telegram бота”””
global bot_application

```
bot_application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

bot_application.add_handler(CommandHandler("start", start_command))
bot_application.add_handler(MessageHandler(
    filters.FORWARDED & (filters.VIDEO | filters.PHOTO | filters.Document.ALL),
    handle_forwarded_message
))

logger.info("Бот ініціалізовано!")
```

if **name** == ‘**main**’:
init_bot()
port = int(os.environ.get(‘PORT’, 10000))
app.run(host=‘0.0.0.0’, port=port)
else:
# Для production (gunicorn)
init_bot()
