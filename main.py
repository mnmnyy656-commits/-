import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from config import BOT_TOKEN, OWNER_ID

def load_data():
    try:
        with open("database.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("database.json", "w") as f:
        json.dump(data, f)

data = load_data()

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🎯 إنشاء روليت", callback_data="create_roulette")]
    ]
    update.message.reply_text("مرحبًا! اضغط على الزر لإنشاء روليت:", reply_markup=InlineKeyboardMarkup(keyboard))

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if query.data == "create_roulette":
        data[str(user_id)] = {"participants": [], "required_channel": None}
        save_data(data)
        context.bot.send_message(chat_id=user_id, text="أرسل رابط القناة التي تريد جعلها شرط للمشاركة:")
        return

    if query.data.startswith("join_roulette_"):
        owner_id = query.data.split("_")[-1]
        roulette = data.get(owner_id)

        if not roulette:
            query.message.reply_text("هذا السحب غير موجود.")
            return

        required_channel = roulette.get("required_channel")
        if required_channel:
            user_status = context.bot.get_chat_member(required_channel, user_id).status
            if user_status not in ["member", "administrator", "creator"]:
                keyboard = [[InlineKeyboardButton("📢 اشترك أولاً", url=f"https://t.me/{required_channel.lstrip('@')}")]]
                query.message.reply_text("❗ عليك الاشتراك بالقناة أولاً.", reply_markup=InlineKeyboardMarkup(keyboard))
                return

        if user_id in roulette["participants"]:
            query.message.reply_text("أنت مشارك بالفعل.")
            return

        roulette["participants"].append(user_id)
        save_data(data)
        query.message.reply_text("✅ تم تسجيلك في السحب!")

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    if str(user_id) in data and data[str(user_id)]["required_channel"] is None:
        data[str(user_id)]["required_channel"] = text
        save_data(data)

        keyboard = [[InlineKeyboardButton("🎉 شارك الآن", callback_data=f"join_roulette_{user_id}")]]
        context.bot.send_message(chat_id=update.message.chat_id, text="تم إعداد السحب، أرسل هذا الزر للمشاركين:", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
