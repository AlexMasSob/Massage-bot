import os
import logging
import hmac
import hashlib
import asyncio
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logging.basicConfig(
format=’%(asctime)s - %(name)s - %(levelname)s - %(message)s’,
level=logging.INFO
)
logger = logging.getLogger(**name**)

TELEGRAM_BOT_TOKEN = os.environ.get(‘TELEGRAM_BOT_TOKEN’, ‘YOUR_BOT_TOKEN’)
WAYFORPAY_SECRET_KEY = os.environ.get(‘WAYFORPAY_SECRET_KEY’, ‘YOUR_SECRET’)
CHANNEL_ID = -1003479515000
COURSE_PRICE = 290

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

app = Flask(**name**)
bot_application = None

def verify_wayforpay_signature(data, signature):
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

async def send_course_videos_async(chat_id: int):
bot = Bot(token=TELEGRAM_BOT_TOKEN)

```
try:
    await bot.send_message(
        chat_id=chat_id,
        text="Vitayu! Dyakuyu za pokupku kursu!\n\nZaraz ty otrymayesh vsi video uroky. Pryyemnogo navchannya!"
    )
    
    await bot.send_message(chat_id=chat_id, text="Vstupne video:")
    await bot.forward_message(
        chat_id=chat_id,
        from_chat_id=CHANNEL_ID,
        message_id=VIDEO_MESSAGE_IDS['intro'],
        protect_content=True
    )
    
    await bot.send_message(chat_id=chat_id, text="Urok 1: Nogy")
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
    
    await bot.send_message(chat_id=chat_id, text="Urok 2: Sidnytsi")
    await bot.forward_message(
        chat_id=chat_id,
        from_chat_id=CHANNEL_ID,
        message_id=VIDEO_MESSAGE_IDS['lesson2'],
        protect_content=True
    )
    
    await bot.send_message(chat_id=chat_id, text="Urok 3: Spyna")
    await bot.forward_message(
        chat_id=chat_id,
        from_chat_id=CHANNEL_ID,
        message_id=VIDEO_MESSAGE_IDS['lesson3'],
        protect_content=True
    )
    
    await bot.send_message(chat_id=chat_id, text="Urok 4: Shyya ta Golova")
    await bot.forward_message(
        chat_id=chat_id,
        from_chat_id=CHANNEL_ID,
        message_id=VIDEO_MESSAGE_IDS['lesson4'],
        protect_content=True
    )
    
    await bot.send_message(chat_id=chat_id, text="Urok 5: Ruky")
    await bot.forward_message(
        chat_id=chat_id,
        from_chat_id=CHANNEL_ID,
        message_id=VIDEO_MESSAGE_IDS['lesson5'],
        protect_content=True
    )
    
    await bot.send_message(chat_id=chat_id, text="Finalne video:")
    await bot.forward_message(
        chat_id=chat_id,
        from_chat_id=CHANNEL_ID,
        message_id=VIDEO_MESSAGE_IDS['final'],
        protect_content=True
    )
    
    await bot.send_message(
        chat_id=chat_id,
        text="Tse vsi uroky kursu! Praktyky regularno. Yakshcho ye pytannya - pysy!"
    )
    
    logger.info(f"Uspishno vidpravleno kurs korystuvachu {chat_id}")
    return True
    
except Exception as e:
    logger.error(f"Pomylka pry vidpravtsi video: {e}")
    return False
```

def send_course_videos(chat_id: int):
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
return loop.run_until_complete(send_course_videos_async(chat_id))
finally:
loop.close()

@app.route(’/webhook/payment’, methods=[‘POST’])
def payment_webhook():
try:
data = request.json
logger.info(f”Otrymano webhook: {data}”)

```
    signature = data.get('merchantSignature', '')
    if not verify_wayforpay_signature(data, signature):
        logger.warning("Nevirnyy pidpys!")
        return jsonify({'error': 'Invalid signature'}), 403
    
    if data.get('transactionStatus') == 'Approved':
        order_ref = data.get('orderReference', '')
        try:
            chat_id = int(order_ref.split('_')[1])
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
            logger.error(f"Pomylka parsyngu orderReference: {e}")
            return jsonify({'error': 'Invalid orderReference'}), 400
    
    return jsonify({'status': 'ok'}), 200
    
except Exception as e:
    logger.error(f"Pomylka v payment_webhook: {e}")
    return jsonify({'error': str(e)}), 500
```

async def start_command(update: Update, context):
chat_id = update.effective_chat.id
await update.message.reply_text(
f”Vitayu!\n\nTse bot dlya kursu samomasazhu.\n\nTviy Telegram ID: {chat_id}\n\nShchob otrymaty dostup do kursu, pereydy na nash sayt ta oplaty kurs.”
)

async def handle_forwarded_message(update: Update, context):
if update.message.forward_from_chat and update.message.forward_from_chat.id == CHANNEL_ID:
message_id = update.message.forward_from_message_id

```
    media_type = "nevidomyy typ"
    if update.message.video:
        media_type = "video"
    elif update.message.photo:
        media_type = "foto"
    elif update.message.document:
        media_type = "dokument"
        
    await update.message.reply_text(
        f"Message ID: {message_id}\nTyp: {media_type}\n\nZberezhy tse chyslo!"
    )
```

@app.route(’/webhook/telegram’, methods=[‘POST’])
def telegram_webhook():
try:
if bot_application is None:
logger.error(“Bot application not initialized”)
return jsonify({‘error’: ‘Bot not ready’}), 503

```
    update = Update.de_json(request.json, bot_application.bot)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(bot_application.process_update(update))
    finally:
        loop.close()
        
    return jsonify({'ok': True}), 200
except Exception as e:
    logger.error(f"Pomylka v telegram_webhook: {e}")
    return jsonify({'error': str(e)}), 500
```

@app.route(’/’)
def home():
return “Bot pratsyuye!”

@app.route(’/health’)
def health():
return jsonify({‘status’: ‘ok’}), 200

def init_bot():
global bot_application
bot_application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
bot_application.add_handler(CommandHandler(“start”, start_command))
bot_application.add_handler(MessageHandler(
filters.FORWARDED & (filters.VIDEO | filters.PHOTO | filters.Document.ALL),
handle_forwarded_message
))
logger.info(“Bot initsializovano!”)

if **name** == ‘**main**’:
init_bot()
port = int(os.environ.get(‘PORT’, 10000))
app.run(host=‘0.0.0.0’, port=port)
else:
init_bot()
