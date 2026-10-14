import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatType
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
OWNER_ID_RAW = os.getenv("OWNER_ID", "").strip()
TARGET_GROUP_ID_RAW = os.getenv("TARGET_GROUP_ID", "").strip()
TOPICS_FILE = Path("topics.json")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

CATEGORIES = {
    "FOTO": {"photo"},
    "VIDEO": {"video", "video_note", "animation"},
    "AUDIO": {"audio", "voice"},
    "DOKUMEN": {"document"},
    "STIKER": {"sticker"},
}


def parse_config():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN belum diisi. Salin .env.example menjadi .env dan isi token.")
    try:
        owner_id = int(OWNER_ID_RAW)
    except ValueError:
        raise SystemExit("OWNER_ID harus berupa angka ID Telegram milikmu.")
    try:
        group_id = int(TARGET_GROUP_ID_RAW)
    except ValueError:
        raise SystemExit("TARGET_GROUP_ID harus berupa angka ID grup Telegram.")
    return owner_id, group_id


OWNER_ID, TARGET_GROUP_ID = parse_config()


def detect_category(message) -> str:
    if message.photo:
        return "FOTO"
    if message.video or message.video_note or message.animation:
        return "VIDEO"
    if message.audio or message.voice:
        return "AUDIO"
    if message.document:
        mime = (message.document.mime_type or "").lower()
        filename = (message.document.file_name or "").lower()
        if mime.startswith("image/"):
            return "FOTO"
        if mime.startswith("video/"):
            return "VIDEO"
        if mime.startswith("audio/") or filename.endswith((".mp3", ".m4a", ".wav", ".flac", ".ogg", ".aac")):
            return "AUDIO"
        if filename.endswith((".zip", ".rar", ".7z", ".tar", ".gz", ".bz2")):
            return "ARSIP"
        return "DOKUMEN"
    if message.sticker:
        return "STIKER"
    return "LAINNYA"


def load_topics() -> dict:
    try:
        return json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_topics(topics: dict) -> None:
    TOPICS_FILE.write_text(json.dumps(topics, indent=2), encoding="utf-8")


async def is_owner_private(update: Update) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    return bool(
        user
        and chat
        and user.id == OWNER_ID
        and chat.type == ChatType.PRIVATE
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner_private(update):
        return
    await update.effective_message.reply_text(
        "Halo! Aku bot arsip file pribadimu.\n\n"
        "Kirim foto, video, audio, dokumen, atau arsip ke chat ini. "
        "Aku akan meneruskannya ke grup tujuan dan mencoba mengelompokkannya ke topik otomatis.\n\n"
        "Perintah:\n"
        "/help - bantuan\n"
        "/status - cek konfigurasi\n"
        "/chatid - lihat ID chat saat ini"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner_private(update):
        return
    await update.effective_message.reply_text(
        "Cara menggunakan:\n"
        "1. Kirim file langsung ke chat pribadi bot ini.\n"
        "2. Bot menentukan kategori file.\n"
        "3. Bot meneruskan file ke grup tujuan.\n\n"
        "Agar tiap kategori masuk ke topik terpisah, aktifkan Topics/Topik di grup "
        "dan jadikan bot admin dengan izin mengirim pesan serta mengelola topik.\n\n"
        "Bot hanya menerima file dari ID pemilik yang disetel di .env."
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner_private(update):
        return
    me = await context.bot.get_me()
    await update.effective_message.reply_text(
        f"Bot aktif: @{me.username}\n"
        f"ID pemilik: {OWNER_ID}\n"
        f"Grup tujuan terkonfigurasi: {TARGET_GROUP_ID}\n"
        "Token tidak ditampilkan."
    )


async def chatid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or user.id != OWNER_ID:
        return
    chat = update.effective_chat
    if chat:
        await update.effective_message.reply_text(f"Chat ID: {chat.id}")


async def get_topic_id(context: ContextTypes.DEFAULT_TYPE, category: str):
    topics = load_topics()
    if category in topics:
        return topics[category]

    # Creating a forum topic requires the destination group to have Topics enabled
    # and the bot to have permission to manage topics.
    topic = await context.bot.create_forum_topic(
        chat_id=TARGET_GROUP_ID,
        name=category,
    )
    topics[category] = topic.message_thread_id
    save_topics(topics)
    return topic.message_thread_id


async def archive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner_private(update):
        return

    message = update.effective_message
    category = detect_category(message)
    try:
        topic_id = await get_topic_id(context, category)
        await context.bot.copy_message(
            chat_id=TARGET_GROUP_ID,
            from_chat_id=message.chat_id,
            message_id=message.message_id,
            message_thread_id=topic_id,
        )
        await message.reply_text(f"✅ File dikirim ke grup, kategori: {category}.")
    except TelegramError as exc:
        logger.warning("Topic/copy failed for %s: %s", category, exc)
        # If the group is not a forum or topic creation is unavailable, fall back
        # to a category label and copy the original message into the group.
        try:
            await context.bot.send_message(
                chat_id=TARGET_GROUP_ID,
                text=f"📁 KATEGORI: {category}",
            )
            await context.bot.copy_message(
                chat_id=TARGET_GROUP_ID,
                from_chat_id=message.chat_id,
                message_id=message.message_id,
            )
            await message.reply_text(
                f"✅ File dikirim ke grup dengan label {category}.\n"
                "Catatan: topik otomatis belum tersedia. Aktifkan Topics dan beri bot izin mengelola topik untuk pengelompokan per topik."
            )
        except TelegramError as fallback_exc:
            logger.exception("Could not send file to destination group")
            await message.reply_text(
                "❌ File belum berhasil dikirim. Periksa ID grup, izin bot sebagai admin, "
                "dan apakah bot sudah ditambahkan ke grup.\n"
                f"Detail: {fallback_exc}"
            )


async def reject_non_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Intentionally silent for non-owner users.
    return


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("chatid", chatid_command))
    file_filter = (
        filters.PHOTO
        | filters.VIDEO
        | filters.AUDIO
        | filters.VOICE
        | filters.VIDEO_NOTE
        | filters.ANIMATION
        | filters.Document.ALL
        | filters.Sticker.ALL
    )
    app.add_handler(MessageHandler(file_filter, archive_file))
    logger.info("Bot is running.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
