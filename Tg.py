import json
import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from site_update import update_site  # Импорт функции обновления сайта

# Состояния диалога
TITLE, IMAGE, LINK = range(3)

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Загрузка товаров
def load_products():
    try:
        with open("products.json", "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Сохранение товаров
def save_products(products):
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("📦 Введи название товара:")
    return TITLE

# Получение названия
async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["title"] = update.message.text
    await update.message.reply_text("🖼 Теперь отправь ссылку на изображение:")
    return IMAGE

# Получение ссылки на изображение
async def get_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["image"] = update.message.text
    await update.message.reply_text("🔗 Теперь отправь партнёрскую ссылку на товар:")
    return LINK

# Получение ссылки на товар
async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["link"] = update.message.text

    # Добавляем товар
    new_product = {
        "title": context.user_data["title"],
        "image": context.user_data["image"],
        "link": context.user_data["link"],
    }

    products = load_products()
    products.insert(0, new_product)
    save_products(products)

    # Обновляем сайт
    update_site()

    await update.message.reply_text("✅ Товар добавлен и сайт обновлён!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Добавление товара отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Запуск бота
def main():
    app = ApplicationBuilder().token("7596662199:AAFSejQfZqwbzz9PpbRDP3ZSGYNPqmccVbk").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
            IMAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_image)],
            LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_link)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("🤖 Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
