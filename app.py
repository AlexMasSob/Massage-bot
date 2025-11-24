import os
import logging
import hmac
import hashlib
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(**name**)

TELEGRAM_BOT_TOKEN = os.environ.get(‘TELEGRAM_BOT_TOKEN’, ‘YOUR_TOKEN’)
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
bot = Bot(token=TELEGRAM_BOT_TOKEN)
updater = None

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

def send_course_videos(chat_id):
try:
bot.send_message(chat_id=chat_id, text=“Vitayu! Dyakuyu za pokupku kursu!”)

```
    bot.send_message(chat_id=chat_id, text="Vstupne video:")
    bot.forward_message(chat_id=chat_id, from_chat_id=CHANNEL_ID, message_id=VIDEO_MESSAGE_IDS['intro'], protect_content=True)
    
    bot.send_message(chat_id=chat_id, text="Urok 1: Nogy")
    bot.forward_message(chat_id=chat_id, from_chat_id=CHANNEL_ID, message_id=VIDEO_MESSAGE_IDS['lesson1_video1'], protect_content=True)
    bot.forward_message(chat_id=chat_id, from_chat_id=CHANNEL_ID, message_id=VIDEO_MESSAGE_IDS['lesson1_video2'], protect_content=True)
    
    bot.send_message(chat_id=chat_id, text="Urok 2: Sidnytsi")
    bot.forward_message(chat_id=chat_id, from_chat_id=CHANNEL_ID, message_id=VIDEO_MESSAGE_IDS['lesson2'], protect_content=True)
    
    bot.send_message(chat_id=chat_id, text="Urok 3: Spyna")
    bot.forward_message(chat_id=chat_id, from_chat_id=CHANNEL_ID, message_id=VIDEO_MESSAGE_IDS['lesson3'], protect_content=True)
    
    bot.send_message(chat_id=chat_id, text="Urok 4: Shyya ta Golova")
    bot.forward_message(chat_id=chat_id, from_chat_id=CHANNEL_ID, message_id=VIDEO_MESSAGE_IDS['lesson4'], protect_content=True)
    
    bot.send_message(chat_id=chat_id, text="Urok 5: Ruky")
    bot.forward_message(chat_id=chat_id, from_chat_id=CHANNEL_ID, message_id=VIDEO_MESSAGE_IDS['lesson5'], protect_content=True)
    
    bot.send_message(chat_id=chat_id, text="Finalne video:")
    bot.forward_message(chat_id=chat_id, from_chat_id=CHANNEL_ID, message_id=VIDEO_MESSAGE_IDS['final'], protect_content=True)
    
    bot.send_message(chat_id=chat_id, text="Tse vsi uroky!")
    
    logger.info("Course sent to user")
    return True
    
except Exception as e:
    logger.error("Error sending videos")
    return False
```

@app.route(’/webhook/payment’, methods=[‘POST’])
def payment_webhook():
try:
data = request.json
logger.info(“Payment webhook received”)

```
    signature = data.get('merchantSignature', '')
    if not verify_wayforpay_signature(data, signature):
        return jsonify({'error': 'Invalid signature'}), 403
    
    if data.get('transactionStatus') == 'Approved':
        order_ref = data.get('orderReference', '')
        try:
            chat_id = int(order_ref.split('_')[1])
            success = send_course_videos(chat_id)
            
            if success:
                response_data = {'orderReference': order_ref, 'status': 'accept', 'time': data.get('time')}
                sign_string = order_ref + ";accept;" + str(data.get('time'))
                response_signature = hmac.new(WAYFORPAY_SECRET_KEY.encode('utf-8'), sign_string.encode('utf-8'), hashlib.md5).hexdigest()
                response_data['signature'] = response_signature
                return jsonify(response_data), 200
            else:
                return jsonify({'error': 'Failed'}), 500
                
        except (IndexError, ValueError):
            return jsonify({'error': 'Invalid order'}), 400
    
    return jsonify({'status': 'ok'}), 200
    
except Exception:
    return jsonify({'error': 'Server error'}), 500
```

def start_command(update, context):
chat_id = update.effective_chat.id
message_text = “Vitayu!\n\nTse bot dlya kursu samomasazhu.\n\nTviy ID: “ + str(chat_id)
update.message.reply_text(message_text)

def handle_forwarded(update, context):
if update.message.forward_from_chat and update.message.forward_from_chat.id == CHANNEL_ID:
message_id = update.message.forward_from_message_id
media_type = “unknown”
if update.message.video:
media_type = “video”
elif update.message.photo:
media_type = “photo”
reply_text = “Message ID: “ + str(message_id) + “\nType: “ + media_type
update.message.reply_text(reply_text)

@app.route(’/webhook/telegram’, methods=[‘POST’])
def telegram_webhook():
try:
if updater is None:
return jsonify({‘error’: ‘Not ready’}), 503
update = Update.de_json(request.json, bot)
updater.dispatcher.process_update(update)
return jsonify({‘ok’: True}), 200
except Exception:
return jsonify({‘error’: ‘Error’}), 500

@app.route(’/’)
def home():
return “Bot works”

@app.route(’/health’)
def health():
return jsonify({‘status’: ‘ok’}), 200

def init_bot():
global updater
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler(“start”, start_command))
dp.add_handler(MessageHandler(Filters.forwarded & (Filters.video | Filters.photo | Filters.document), handle_forwarded))
logger.info(“Bot initialized”)

if **name** == ‘**main**’:
init_bot()
port = int(os.environ.get(‘PORT’, 10000))
app.run(host=‘0.0.0.0’, port=port, debug=False)
