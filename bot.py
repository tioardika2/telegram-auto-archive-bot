import asyncio
import json
import logging
import os
import sys
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
TOPICS_FILE = Path(__file__).resolve().parent / "topics.json"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def parse_config():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN belum diisi. Periksa file .env.")
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


def print_banner():
    """Tampilkan banner besar saat bot mulai dijalankan di Termux."""
    cyan = "\033[96m"
    green = "\033[1;92m"
    white = "\033[1;97m"
    reset = "\033[0m"
    clear = "\033[2J\033[H"

    print(clear, end="")
    print(cyan + r"""
██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗██╗███╗   ██╗ ██████╗
██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝██║████╗  ██║██╔════╝
██║    ██║██║   ██║██████╔╝█████╔╝ ██║██╔██╗ ██║██║  ███╗
██║    ██║██║   ██║██╔══██╗██╔═██╗ ██║██║╚██╗██║██║   ██║
╚██████╔╝╚██████╔╝██║  ██║██║  ██╗██║██║ ╚████║╚██████╔╝
 ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝
""" + reset)
    print(white + "          TELEGRAM AUTO ARCHIVE BOT" + reset)
    print(green + "                 ● WORKING ●" + reset)
    print("  Status : Starting...")
    print("  Mode   : Auto Archive")
    print("  Access : Owner only")
    print("-" * 48)


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
        if mime.startswith("audio/") or filename.endswith(
            (".mp3", ".m4a", ".wav", ".flac", ".ogg", ".aac")
        ):
            return "AUDIO"
        if filename.endswith((".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz")):
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
    TOPICS_FILE.write_text(
        json.dumps(topics, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


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
        "Aku akan meneruskannya ke grup tujuan dan mencoba mengelompokkannya "
        "ke topik otomatis.\n\n"
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
        "Agar tiap kategori masuk ke topik terpisah, aktifkan Topics/Topik "
        "di grup dan jadikan bot admin dengan izin mengelola topik.\n\n"
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
                "Catatan: topik otomatis belum tersedia. Aktifkan Topics dan "
                "beri bot izin mengelola topik untuk pengelompokan per topik."
            )
        except TelegramError as fallback_exc:
            logger.exception("Could not send file to destination group")
            await message.reply_text(
                "❌ File belum berhasil dikirim. Periksa ID grup, izin bot "
                "sebagai admin, dan apakah bot sudah ditambahkan ke grup.\n"
                f"Detail: {fallback_exc}"
            )



def category_for_local_file(file_path: Path) -> str:
    """Tentukan kategori sederhana berdasarkan ekstensi file lokal."""
    suffix = file_path.suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic"}:
        return "FOTO"
    if suffix in {".mp4", ".mov", ".mkv", ".avi", ".webm", ".3gp", ".mpeg"}:
        return "VIDEO"
    if suffix in {".mp3", ".m4a", ".wav", ".flac", ".ogg", ".aac", ".opus"}:
        return "AUDIO"
    if suffix in {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"}:
        return "ARSIP"
    if suffix in {".apk"}:
        return "LAINNYA"
    if suffix in {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt",
                  ".xls", ".xlsx", ".ppt", ".pptx", ".csv"}:
        return "DOKUMEN"
    return "DOKUMEN"


async def send_local_file(file_path: Path) -> None:
    """Kirim file dari Termux ke topik kategori yang sama dengan auto-archive."""
    from telegram import Bot

    if not file_path.is_file():
        raise SystemExit(
            f"File tidak ditemukan: {file_path}\\n"
            "Periksa nama file, lokasi, dan izin akses penyimpanan Termux."
        )

    category = category_for_local_file(file_path)
    try:
        async with Bot(token=BOT_TOKEN) as bot:
            # Gunakan file topics.json yang sama dengan bot otomatis.
            thread_id = await get_or_create_topic_for_cli(bot, category)

            with file_path.open("rb") as file_obj:
                sent = await bot.send_document(
                    chat_id=TARGET_GROUP_ID,
                    document=file_obj,
                    filename=file_path.name,
                    caption=f"📁 Arsip dari Termux | Kategori: {category}",
                    message_thread_id=thread_id,
                )

        print("\\n✅ FILE BERHASIL DIKIRIM KE TOPIK KATEGORI")
        print(f"Nama      : {file_path.name}")
        print(f"Kategori  : {category}")
        print(f"Topik ID  : {thread_id}")
        print(f"Ukuran    : {file_path.stat().st_size:,} byte")
        print(f"Message ID: {sent.message_id}\\n")
    except TelegramError as exc:
        print(f"\\n❌ Gagal mengirim file ke topik {category}: {exc}")
        print("File tidak dialihkan ke General agar tidak terpisah dari kategori.")
        print("Pastikan grup memiliki Topics dan bot boleh mengelola topik serta mengirim file.")
        raise SystemExit(1)


async def get_or_create_topic_for_cli(bot, category: str):
    """Ambil ID topik tersimpan atau buat topik kategori baru untuk pengiriman CLI."""
    topics = load_topics()
    if category in topics:
        return int(topics[category])

    topic = await bot.create_forum_topic(chat_id=TARGET_GROUP_ID, name=category)
    topics[category] = topic.message_thread_id
    save_topics(topics)
    return topic.message_thread_id


async def send_folder(folder_path: Path) -> None:
    """Kirim semua file dalam folder (tidak termasuk subfolder) ke grup."""
    if not folder_path.is_dir():
        raise SystemExit(f"Folder tidak ditemukan: {folder_path}")

    files = sorted(p for p in folder_path.iterdir() if p.is_file() and not p.name.startswith("."))
    if not files:
        raise SystemExit(f"Tidak ada file di folder: {folder_path}")

    print(f"Folder: {folder_path}")
    print(f"Jumlah file: {len(files)}")
    print("File akan dikirim satu per satu. Tekan Ctrl+C untuk membatalkan.\\n")

    success = 0
    failed = 0
    for index, file_path in enumerate(files, start=1):
        print(f"[{index}/{len(files)}] Mengirim: {file_path.name}")
        try:
            await send_local_file(file_path)
            success += 1
        except SystemExit:
            failed += 1
        except Exception as exc:
            print(f"Gagal: {exc}")
            failed += 1
    print(f"\\nSelesai. Berhasil: {success}, gagal: {failed}, total: {len(files)}")


def cli_send_mode() -> bool:
    """Perintah CLI: --send untuk file, --send-folder untuk semua file dalam folder."""
    if len(sys.argv) >= 2 and sys.argv[1] == "--send-folder":
        if len(sys.argv) < 3:
            print('Cara pakai: python bot.py --send-folder "/sdcard/Download/Arsip"')
            raise SystemExit(1)
        folder_path = Path(" ".join(sys.argv[2:])).expanduser()
        asyncio.run(send_folder(folder_path))
        return True

    if len(sys.argv) >= 2 and sys.argv[1] == "--send":
        if len(sys.argv) < 3:
            print('Cara pakai: python bot.py --send "/sdcard/Download/nama file.pdf"')
            raise SystemExit(1)
        file_path = Path(" ".join(sys.argv[2:])).expanduser()
        asyncio.run(send_local_file(file_path))
        return True
    return False


def main():
    print_banner()
    print("\\nPILIH MODE:")
    print("1. Backup melalui bot Telegram (menerima file dari chat pribadi bot)")
    print("2. Backup langsung dari folder HP melalui Termux")
    print("0. Keluar")

    try:
        choice = input("\\nMasukkan pilihan [0/1/2]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\\nDibatalkan.")
        return

    if choice == "0":
        print("Keluar.")
        return
    if choice == "2":
        folder_text = input('Masukkan lokasi folder yang ingin di-backup: ').strip()
        folder_text = folder_text.strip('"').strip("'")
        if not folder_text:
            print("Lokasi folder tidak boleh kosong.")
            return
        asyncio.run(send_folder(Path(folder_text).expanduser()))
        return
    if choice != "1":
        print("Pilihan tidak valid. Jalankan python bot.py lalu pilih 0, 1, atau 2.")
        return

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
    if not cli_send_mode():
        main()
