# Telegram Auto Archive Bot

Bot Telegram pribadi untuk meneruskan file ke grup dan mengelompokkannya berdasarkan jenis file.

## Fitur

- Hanya menerima file dari ID pemilik yang ditentukan di `.env`.
- Mengenali foto, video, audio, dokumen, stiker, arsip, dan file lain.
- Mencoba membuat topik forum otomatis berdasarkan kategori.
- Jika grup belum mendukung topik, bot mencoba mengirim label kategori lalu file.
- Token disimpan di `.env`, bukan di kode.

## Kebutuhan

- Python 3.10 atau lebih baru
- Bot yang dibuat melalui [@BotFather](https://t.me/BotFather)
- Grup tujuan yang sudah ditambahkan bot sebagai admin
- Untuk topik otomatis: aktifkan Topics di grup dan izinkan bot mengelola topik

## Instalasi di Android dengan Termux

```bash
pkg update && pkg upgrade -y
pkg install python nano git -y
git clone https://github.com/USERNAME/telegram-auto-archive-bot.git
cd telegram-auto-archive-bot
pip install -r requirements.txt
cp .env.example .env
nano .env
python bot.py
```

Ganti URL GitHub di atas dengan URL repository milikmu. Jika menjalankan dari folder ZIP, lewati perintah `git clone`.

Isi `.env`:
- `BOT_TOKEN`: token dari BotFather
- `OWNER_ID`: ID angka akun Telegram pemilik
- `TARGET_GROUP_ID`: ID angka grup tujuan, biasanya diawali `-100`

## Mendapatkan ID grup

Tambahkan bot ke grup sebagai admin. Untuk mendapatkan ID grup, cara yang paling mudah adalah menjalankan bot sementara dengan `TARGET_GROUP_ID` diisi nilai sementara yang valid, lalu kirim `/chatid` di grup. Alternatifnya, gunakan bot ID-info tepercaya untuk membaca ID grup. Jangan pernah membagikan token bot.

## Menjalankan bot

```bash
python bot.py
```

Kirim `/start` ke bot pribadi, lalu kirim file. Bot akan mencoba membuat topik dengan nama kategori di grup forum.

## Menjaga bot tetap aktif

Termux cocok untuk pengujian, tetapi Android dapat menghentikan proses di latar belakang. Untuk 24/7 yang lebih stabil, pindahkan proyek ke hosting/server yang mendukung proses Python jangka panjang. Paket gratis dapat memiliki batasan dan tidak selalu menjamin uptime.

## Keamanan

- Jangan commit `.env` atau mengirim token bot kepada siapa pun.
- Jika token bocor, buat ulang melalui BotFather.
- Jangan menghapus batasan `OWNER_ID` jika bot harus digunakan pribadi.
- Simpan salinan cadangan konfigurasi di tempat aman.

## Catatan

Ini adalah template awal. Uji dengan file non-penting terlebih dahulu dan pastikan bot memiliki izin yang benar di grup tujuan.
