import asyncio
import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

def build_card_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Hiện thông tin", callback_data="action_info"),
            InlineKeyboardButton("Cập nhật", callback_data="action_update"),
        ],
        [
            InlineKeyboardButton("Done kèo", callback_data="action_done"),
            InlineKeyboardButton("Hủy kèo", callback_data="action_cancel"),
        ],
        [
            InlineKeyboardButton("Quay lại", callback_data="action_back"),
        ],
    ])

def build_card_text(bot_label: str, status: str = "Đang chờ xử lý") -> str:
    return (
        f"📌 *CARD QUẢN LÝ — {bot_label}*\n"
        f"• Trạng thái: *{status}*\n"
        f"• Chọn thao tác bên dưới để xử lý:"
    )

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot_label = context.bot_data.get("bot_label", "BOT")
    if update.message:
        await update.message.reply_text(
            text=build_card_text(bot_label),
            reply_markup=build_card_keyboard(),
            parse_mode="Markdown",
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()

    bot_label = context.bot_data.get("bot_label", "BOT")
    data = query.data

    status_map = {
        "action_info": "Đang xem thông tin",
        "action_update": "Đã cập nhật kèo",
        "action_done": "Đã Done kèo",
        "action_cancel": "Đã Hủy kèo",
        "action_back": "Đã quay lại menu chính",
    }
    new_status = status_map.get(data, "Đã thao tác")

    await query.edit_message_text(
        text=build_card_text(bot_label, status=new_status),
        reply_markup=build_card_keyboard(),
        parse_mode="Markdown",
    )

async def run_single_bot(token: str, bot_label: str) -> None:
    app = Application.builder().token(token).build()
    app.bot_data["bot_label"] = bot_label
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))

    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

async def main() -> None:
    token1 = os.getenv("BOT1_TOKEN", "").strip()
    token2 = os.getenv("BOT2_TOKEN", "").strip()

    tasks = []
    if token1:
        tasks.append(run_single_bot(token1, "@ripfacebookpro_bot"))
    if token2:
        tasks.append(run_single_bot(token2, "@KOBiMedia_Bot"))

    if not tasks:
        raise RuntimeError("Thiếu biến môi trường BOT1_TOKEN hoặc BOT2_TOKEN")

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main()) 
