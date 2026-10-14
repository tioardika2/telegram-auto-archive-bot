#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"
if [ ! -f .env ]; then
  echo "File .env belum ada. Salin .env.example menjadi .env dan isi konfigurasi."
  exit 1
fi
python bot.py
