from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import csv
import os

# ================= CONFIG =================
BOT_TOKEN = "8176795153:AAEp-3zvMUvlLxsEJC0Zom-Lp2mt_0jW7UY"
ADMIN_ID = 6643703017  # Replace with your Telegram ID

# ================= STORAGE =================
user_language = {}
user_data = {}
user_step = {}

pending_questions = {}
question_counter = 1

# ================= TEXTS =================
TEXTS = {
    "en": {
        "greet": "Hello! 👋\nThank you for taking the time to fill out this form.\nPlease answer the questions below.",
        "who": "Please let us know who is filling this form:",
        "phone": "Kindly provide your contact phone number:",
        "manual_location": "Please enter your full address manually:",
        "child": "Please enter the child’s full name:",
        "age": "Could you kindly share the child’s age:",
        "grade": "Please enter the child’s grade:",
        "start_time": "What time do lessons usually start?",
        "end_time": "What time do lessons usually end?",
        "bus": "Please mention the nearest bus stop for convenient pickup:",
        "school": "Please tell us the name or number of the school the child attends:",
        "geo_location": "Please share your location using the map:",
        "thanks": "Thank you very much! 🌟\nYour information has been successfully saved.\n\nYou may now ask questions or provide suggestions. Our managers will respond to you via this bot.",
        "question_received": "✅ Thank you. Your question/suggestion has been received.",
        "answer": "📩 Answer to your question/suggestion:",
        "invalid": "❗Invalid input. Please try again.",
        "back": "Back",
        "share_location": "📍 Share Location",
        "ask_question": "Ask Question / Offer",
        "start_again": "Start Again"
    },
    "uz": {
        "greet": "Assalomu alaykum! 👋\nFormani to‘ldirayotganingiz uchun rahmat.\nIltimos, savollarga javob bering.",
        "who": "Iltimos, kim shaklni to‘ldirayotganini yozing:",
        "phone": "Bog‘lanish uchun telefon raqamingizni kiriting:",
        "manual_location": "Iltimos, to‘liq manzilingizni kiriting:",
        "child": "Farzandingizning to‘liq ismini yozing:",
        "age": "Farzandingizning yoshi:",
        "grade": "Farzandingizning sinfini kiriting:",
        "start_time": "Dars boshlanish vaqti:",
        "end_time": "Maktabdan chiqish vaqti:",
        "bus": "Uyingizga eng yaqin avtobus bekatini ko‘rsating:",
        "school": "Maktab raqami yoki nomini kiriting:",
        "geo_location": "Iltimos, xaritada joylashuvingizni ulashing:",
        "thanks": "Katta rahmat! 🌟\nMa’lumotlaringiz muvaffaqiyatli saqlandi.\n\nSavollar yoki takliflar berishingiz mumkin. Bizning menejerlarimiz siz bilan ushbu bot orqali bog‘lanadi.",
        "question_received": "✅ Rahmat. Savolingiz/taklifingiz qabul qilindi.",
        "answer": "📩 Savolingizga/taklifingizga javob:",
        "invalid": "❗Xato javob. Iltimos qaytadan urinib ko‘ring.",
        "back": "Orqaga",
        "share_location": "📍 Joylashuvni ulash",
        "ask_question": "Savol berish / Taklif",
        "start_again": "Yana boshlash"
    },
    "ru": {
        "greet": "Здравствуйте! 👋\nСпасибо за заполнение формы.\nПожалуйста, ответьте на вопросы ниже.",
        "who": "Пожалуйста, укажите, кто заполняет эту форму:",
        "phone": "Введите контактный номер телефона:",
        "manual_location": "Пожалуйста, введите полный адрес:",
        "child": "Полное имя ребёнка:",
        "age": "Возраст ребёнка:",
        "grade": "Класс ребёнка:",
        "start_time": "Время начала занятий:",
        "end_time": "Время окончания занятий:",
        "bus": "Ближайшая автобусная остановка:",
        "school": "Название или номер школы:",
        "geo_location": "Пожалуйста, поделитесь своим местоположением на карте:",
        "thanks": "Большое спасибо! 🌟\nВаши данные успешно сохранены.\n\nВы можете задать вопросы или оставить предложения. Наши менеджеры свяжутся с вами через этот бот.",
        "question_received": "✅ Спасибо. Ваш вопрос/предложение получено.",
        "answer": "📩 Ответ на ваш вопрос/предложение:",
        "invalid": "❗Неверный ввод. Пожалуйста, попробуйте снова.",
        "back": "Назад",
        "share_location": "📍 Поделиться местоположением",
        "ask_question": "Задать вопрос / Предложение",
        "start_again": "Начать заново"
    }
}

# ================= STEPS =================
STEPS = ["who", "phone", "manual_location", "child", "age", "grade", "start_time", "end_time", "bus", "school", "geo_location"]

# ================= BUTTONS =================
LANGUAGE_KEYBOARD = ReplyKeyboardMarkup(
    [["Uzbek"], ["Russian"], ["English"]],
    resize_keyboard=True,
    one_time_keyboard=True
)

WHO_BUTTONS = {
    "en": [["Mother", "Father", "Other"]],
    "uz": [["Ona", "Ota", "Boshqa"]],
    "ru": [["Мама", "Папа", "Другое"]]
}

# ================= CSV =================
def save_to_csv(user_id, lang, data):
    os.makedirs("data", exist_ok=True)
    with open("data/student_answers.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            user_id, lang,
            data.get("who",""), data.get("phone",""), data.get("manual_location",""),
            data.get("child",""), data.get("age",""), data.get("grade",""),
            data.get("start_time",""), data.get("end_time",""),
            data.get("bus",""), data.get("school",""), data.get("geo_location","")
        ])

def save_user_id(user_id, lang):
    os.makedirs("data", exist_ok=True)
    try:
        with open("data/user_ids.csv", "r", encoding="utf-8") as f:
            ids = {line.strip().split(",")[0]: line.strip().split(",")[1] for line in f if "," in line}
    except FileNotFoundError:
        ids = {}
    if str(user_id) not in ids:
        with open("data/user_ids.csv", "a", encoding="utf-8") as f:
            f.write(f"{user_id},{lang}\n")

# ================= VALIDATION =================
def validate_input(key, text):
    text = text.strip()
    if not text:
        return False
    if key == "phone":
        return text.replace(" ","").replace("+","").replace("-","").isdigit() and len(text) >= 5
    if key in ["age", "grade"]:
        return any(c.isdigit() for c in text)
    if key in ["start_time","end_time"]:
        return "-" not in text and text  # just non-empty
    if key == "who":
        return text.lower() in [
            "mother","father","other",
            "ona","ota","boshqa",
            "мама","папа","другое"
        ]
    return True

# ================= KEYBOARD =================
def get_keyboard_for_step(lang, key):
    back_text = TEXTS[lang]["back"]
    if key == "who":
        buttons = WHO_BUTTONS[lang][0] + [back_text]
        return ReplyKeyboardMarkup([buttons], resize_keyboard=True, one_time_keyboard=True)
    elif key == "geo_location":
        buttons = [[KeyboardButton(TEXTS[lang]["share_location"], request_location=True)], [back_text]]
        return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
    else:
        return ReplyKeyboardMarkup([[back_text]], resize_keyboard=True, one_time_keyboard=True)

# ================= /start =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_step.pop(user_id, None)
    user_data.pop(user_id, None)
    user_language.pop(user_id, None)
    await update.message.reply_text(
        "Choose your language / Tilni tanlang / Выберите язык:",
        reply_markup=LANGUAGE_KEYBOARD
    )

# ================= ADMIN ANSWER =================
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /answer <question_id> <reply>")
        return
    qid = int(context.args[0])
    reply = " ".join(context.args[1:])
    if qid not in pending_questions:
        await update.message.reply_text("Question ID not found.")
        return
    user_id = pending_questions[qid]["user_id"]
    lang = pending_questions[qid]["lang"]
    await context.bot.send_message(chat_id=user_id, text=f"{TEXTS[lang]['answer']}\n\n{reply}")
    del pending_questions[qid]
    await update.message.reply_text(f"✅ Answer sent for Question #{qid}")

# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast Your message here")
        return
    message_text = " ".join(context.args)
    try:
        with open("data/user_ids.csv", "r", encoding="utf-8") as f:
            users = [line.strip().split(",") for line in f if "," in line]
            user_ids = [(int(uid), lang) for uid, lang in users]
    except FileNotFoundError:
        await update.message.reply_text("No users found.")
        return
    for uid, lang in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=message_text)
        except Exception as e:
            print(f"Failed to send message to {uid}: {e}")
    await update.message.reply_text(f"Broadcast sent to {len(user_ids)} users.")

# ================= MAIN HANDLER =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global question_counter
    user_id = update.message.from_user.id
    text = update.message.text if update.message else None
    location = update.message.location if update.message else None

    user_data.setdefault(user_id,{})
    user_step.setdefault(user_id,0)

    # Language selection
    if user_id not in user_language:
        if text and text.lower() in ["english","uzbek","russian"]:
            lang_map = {"english":"en","uzbek":"uz","russian":"ru"}
            lang = lang_map[text.lower()]
            user_language[user_id] = lang
            user_data[user_id] = {}
            user_step[user_id] = 0
            await update.message.reply_text(TEXTS[lang]["greet"])
            await update.message.reply_text(TEXTS[lang]["who"], reply_markup=get_keyboard_for_step(lang,"who"))
        else:
            await update.message.reply_text("Please choose a language using the buttons.", reply_markup=LANGUAGE_KEYBOARD)
        return

    lang = user_language[user_id]
    step_index = user_step[user_id]

    # Finished form
    if step_index == "finished":
        if text:
            qid = question_counter
            question_counter += 1
            pending_questions[qid] = {"user_id": user_id, "lang": lang, "text": text}
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📩 New Question #{qid}\nFrom User ID: {user_id}\nLanguage: {lang}\n\nQuestion/Suggestion:\n{text}\n\nReply using:\n/answer {qid} your reply"
            )
            await update.message.reply_text(TEXTS[lang]["question_received"])
        return

    key = STEPS[step_index]

    # Back button
    if text == TEXTS[lang]["back"]:
        if step_index > 0:
            user_step[user_id] -= 1
            key = STEPS[user_step[user_id]]
            await update.message.reply_text(TEXTS[lang][key], reply_markup=get_keyboard_for_step(lang,key))
        return

    # Geo location
    if key == "geo_location":
        if location:
            user_data[user_id]["geo_location"] = f"{location.latitude},{location.longitude}"
            user_step[user_id] += 1
        else:
            await update.message.reply_text(f"{TEXTS[lang]['invalid']}\n{TEXTS[lang]['geo_location']}", reply_markup=get_keyboard_for_step(lang,key))
            return
    elif key == "who":
        if text and validate_input(key, text):
            user_data[user_id]["who"] = text.strip()
            user_step[user_id] += 1
        else:
            await update.message.reply_text(f"{TEXTS[lang]['invalid']}\n{TEXTS[lang]['who']}", reply_markup=get_keyboard_for_step(lang,key))
            return
    else:
        if text and validate_input(key, text):
            user_data[user_id][key] = text.strip()
            user_step[user_id] += 1
        else:
            await update.message.reply_text(f"{TEXTS[lang]['invalid']}\n{TEXTS[lang][key]}", reply_markup=get_keyboard_for_step(lang,key))
            return

    # Next question or finish
    if user_step[user_id] < len(STEPS):
        next_key = STEPS[user_step[user_id]]
        await update.message.reply_text(TEXTS[lang][next_key], reply_markup=get_keyboard_for_step(lang,next_key))
    else:
        # Form complete
        save_to_csv(user_id, lang, user_data[user_id])
        save_user_id(user_id, lang)

        keyboard = [
            [InlineKeyboardButton(TEXTS[lang]["ask_question"], callback_data="ask_question")],
            [InlineKeyboardButton(TEXTS[lang]["start_again"], callback_data="start_again")]
        ]
        await update.message.reply_text(TEXTS[lang]["thanks"], reply_markup=InlineKeyboardMarkup(keyboard))
        user_step[user_id] = "finished"

# ================= CALLBACK HANDLER =================
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = user_language.get(user_id, "en")

    if query.data == "start_again":
        user_step.pop(user_id,None)
        user_data.pop(user_id,None)
        user_language.pop(user_id,None)
        await query.message.reply_text("Choose your language / Tilni tanlang / Выберите язык:", reply_markup=LANGUAGE_KEYBOARD)
    elif query.data == "ask_question":
        user_step[user_id] = "finished"
        await query.message.reply_text(TEXTS[lang]["ask_question"] + "\n\nYour question or suggestion will be answered via this bot.", reply_markup=ReplyKeyboardRemove())

# ================= RUN =================
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("answer", answer))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.LOCATION, handle_message))
app.add_handler(CallbackQueryHandler(handle_callback))
app.run_polling()
