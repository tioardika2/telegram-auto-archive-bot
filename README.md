# Telegram Auto Archive Bot

Bot Telegram berbasis Python untuk mengarsipkan file ke grup Telegram menggunakan topik kategori. Bot dirancang agar dapat dijalankan dari Android melalui Termux.

## Fitur

- Menerima file yang dikirim ke chat pribadi bot dan meneruskannya ke grup arsip.
- Mengelompokkan file berdasarkan kategori seperti **FOTO**, **VIDEO**, **AUDIO**, **DOKUMEN**, **ARSIP**, **STIKER**, dan **LAINNYA** (bergantung pada jenis file yang didukung kode).
- Mengirim file lokal dari Termux ke grup tanpa perlu membuka aplikasi Telegram.
- Mengirim semua file yang berada langsung di satu folder dengan satu perintah.
- Menu pilihan saat menjalankan `python bot.py`:
  - `1` — menjalankan bot Telegram untuk menerima file dari chat.
  - `2` — mengirim file dalam folder lokal melalui Termux.
  - `0` — keluar.
- Banner terminal dan pesan hasil pengiriman.

> Catatan: menu, nama kategori, dan kemampuan membuat topik bergantung pada versi `bot.py` yang dipasang. Gunakan file `bot.py` terbaru dari repositori ini.

## Persyaratan

- Akun Telegram.
- Bot Telegram yang dibuat melalui [@BotFather](https://t.me/BotFather).
- Grup Telegram tujuan. Untuk menggunakan topik kategori, grup harus mengaktifkan **Topics/Forum**.
- Android dengan Termux atau komputer yang memiliki Python 3.
- Koneksi internet.
- Bot harus ditambahkan ke grup tujuan dan memiliki izin mengirim pesan/file. Untuk membuat topik secara otomatis, bot juga memerlukan izin pengelolaan topik.

## 1. Buat bot Telegram

1. Buka Telegram dan cari [@BotFather](https://t.me/BotFather).
2. Kirim `/newbot`.
3. Ikuti instruksi untuk memberi nama dan username bot.
4. Simpan token yang diberikan BotFather secara pribadi.
5. Jangan pernah memublikasikan token, mengirimnya ke orang lain, atau memasukkannya ke README.

Jika token pernah terungkap, buka BotFather dan cabut/ganti token tersebut.

## 2. Siapkan grup arsip

1. Buat grup Telegram atau pilih grup yang akan digunakan.
2. Jika ingin menggunakan topik, aktifkan **Topics/Forum** pada pengaturan grup.
3. Tambahkan bot ke grup.
4. Pastikan bot memiliki izin mengirim pesan dan dokumen. Jika bot perlu membuat topik kategori otomatis, berikan izin mengelola topik.
5. Dapatkan ID grup yang benar dan masukkan ke `.env` sebagai `TARGET_GROUP_ID`.

ID grup supergroup biasanya berupa angka negatif yang diawali `-100`, tetapi gunakan ID grup milik Anda sendiri.

## 3. Instal Termux dan siapkan proyek

Pasang Termux dari sumber tepercaya, lalu buka Termux dan jalankan:

```bash
pkg update && pkg upgrade -y
pkg install python nano -y
termux-setup-storage
```

Saat Android meminta izin akses file, pilih **Izinkan**.

Buat folder proyek jika belum ada:

```bash
mkdir -p ~/telegram-auto-archive-bot
cd ~/telegram-auto-archive-bot
```

Letakkan file proyek dari repositori ke folder tersebut, minimal `bot.py` dan `requirements.txt`. Cara termudah adalah mengunduh repositori sebagai ZIP dari GitHub, mengekstraknya, lalu menyalin isi folder proyek ke `~/telegram-auto-archive-bot`.

Instal dependensi:

```bash
pip install -r requirements.txt
```

Jika repositori tidak menyediakan `requirements.txt`, periksa instruksi instalasi pada repositori sebelum memasang paket secara manual.

## 4. Buat dan edit file `.env`

Dari folder proyek, jalankan:

```bash
cp .env.example .env
nano .env
```

Jika repositori memakai nama contoh lain, buat file `.env` sendiri. Isi dengan konfigurasi Anda, misalnya:

```dotenv
BOT_TOKEN=ISI_TOKEN_BOT_ANDA
OWNER_ID=ISI_ID_TELEGRAM_ANDA
TARGET_GROUP_ID=ISI_ID_GRUP_TUJUAN
```

Ganti semua nilai contoh dengan nilai yang benar. Jangan menambahkan tanda kutip kecuali memang dibutuhkan oleh format konfigurasi.

Keterangan:

- `BOT_TOKEN`: token rahasia yang diberikan BotFather.
- `OWNER_ID`: ID akun Telegram yang diizinkan mengirim file ke bot (jika digunakan oleh versi bot).
- `TARGET_GROUP_ID`: ID grup tujuan pengarsipan.

Simpan di Nano:
1. Tekan `CTRL + O`.
2. Tekan `Enter`.
3. Tekan `CTRL + X`.

Pastikan `.env` berada di folder yang sama dengan `bot.py`. Jangan unggah `.env` ke GitHub. Tambahkan `.env` ke `.gitignore`.

Contoh `.gitignore`:

```gitignore
.env
__pycache__/
*.pyc
```

## 5. Jalankan bot dan pilih mode

Dari folder proyek:

```bash
cd ~/telegram-auto-archive-bot
python bot.py
```

Pada versi yang memiliki menu interaktif, terminal akan menampilkan pilihan berikut.

### Pilihan `1` — Backup melalui bot Telegram

1. Ketik `1`, lalu tekan Enter.
2. Biarkan Termux tetap berjalan.
3. Buka Telegram dan masuk ke chat pribadi bot.
4. Kirim foto, video, audio, dokumen, atau file yang didukung.
5. Bot akan mencoba meneruskan file ke grup arsip dan kategori yang sesuai.

Pilihan ini memerlukan aplikasi Telegram untuk mengirim file ke chat bot. Setelah bot aktif, proses pengarsipan dilakukan oleh bot.

### Pilihan `2` — Backup langsung dari folder HP melalui Termux

1. Ketik `2`, lalu tekan Enter.
2. Masukkan path folder yang ingin diarsipkan. Contoh:

   ```text
   /storage/emulated/0/Download/Arsip
   ```

3. Tekan Enter.
4. Bot akan mengirim file satu per satu ke grup tujuan.
5. Periksa ringkasan jumlah file yang berhasil dan gagal.

Contoh: jika file yang ingin dikirim berada di folder `Download/Arsip`, perintah ini juga dapat dijalankan langsung:

```bash
python bot.py --send-folder "/storage/emulated/0/Download/Arsip"
```

Perintah untuk satu file:

```bash
python bot.py --send "/storage/emulated/0/Download/foto.jpg"
```

Ganti nama file dan path dengan lokasi sebenarnya. Gunakan tanda kutip jika path mengandung spasi.

**Penting:** mode folder hanya memproses file yang berada langsung di folder tersebut; file di dalam subfolder tidak otomatis ikut dikirim, kecuali versi kode secara eksplisit mendukung pemrosesan rekursif.

### Pilihan `0` — Keluar

Ketik `0`, lalu tekan Enter untuk keluar tanpa menjalankan proses backup.

## 6. Topik kategori di grup

Jika grup menggunakan Topics/Forum, bot dapat mengelompokkan file ke topik kategori. Pengiriman dari Termux menggunakan pemetaan topik yang disimpan oleh versi bot, misalnya dalam `topics.json`.

- Jangan menghapus `topics.json` jika ingin mempertahankan pemetaan topik yang sudah tersimpan.
- Jalankan bot dan perintah pengiriman dari folder proyek yang sama.
- Pastikan `TARGET_GROUP_ID` mengarah ke grup yang sama.
- Jika topik dibuat secara manual, pemetaan lokal mungkin perlu disesuaikan.
- Jika bot tidak memiliki izin mengelola topik, pembuatan topik otomatis dapat gagal.

Nama kategori ditentukan oleh aturan ekstensi file pada kode. Tidak semua ekstensi atau jenis media pasti dikenali oleh setiap versi.

## 7. Menghentikan dan menjalankan ulang

- Untuk menghentikan proses yang sedang berjalan, tekan `CTRL + C` di Termux.
- Untuk menjalankan ulang, gunakan:

  ```bash
  cd ~/telegram-auto-archive-bot
  python bot.py
  ```

Termux harus tetap berjalan dan ponsel harus memiliki koneksi internet selama pengarsipan berlangsung. Android dapat menghentikan proses latar belakang karena penghematan baterai; pengaturan baterai yang mengizinkan Termux berjalan di latar belakang dapat membantu.

## 8. Mengatasi masalah

### `BOT_TOKEN atau TARGET_GROUP_ID belum diatur`

- Pastikan file `.env` ada di folder yang sama dengan `bot.py`.
- Pastikan nama variabel ditulis persis seperti contoh.
- Periksa apakah nilainya benar, tanpa spasi yang tidak perlu.

### `File tidak ditemukan`

- Periksa path dan nama file.
- Jalankan `termux-setup-storage` dan izinkan akses penyimpanan.
- Gunakan path lengkap, misalnya `/storage/emulated/0/Download/Arsip`.

### `Permission denied`

- Periksa izin penyimpanan Android untuk Termux.
- Pastikan file dapat dibaca.
- Jika file berada di folder aplikasi yang dilindungi Android, salin ke folder Download terlebih dahulu.

### `Chat not found`

- Periksa `TARGET_GROUP_ID`.
- Pastikan bot sudah ditambahkan ke grup tujuan.
- Pastikan ID berasal dari grup yang benar.

### `Forbidden` atau bot tidak bisa mengirim

- Periksa izin bot untuk mengirim pesan dan dokumen.
- Pastikan bot belum dikeluarkan atau dibatasi oleh admin grup.

### File tidak masuk ke topik yang benar

- Pastikan Topics/Forum aktif.
- Pastikan `topics.json` dan `.env` yang digunakan berasal dari folder proyek yang sama.
- Pastikan ID grup yang digunakan benar.
- Periksa log error di Termux. Jangan mengirim token saat meminta bantuan.

### Bot tidak merespons

- Pastikan Termux menampilkan pesan bahwa aplikasi bot sudah dimulai.
- Periksa koneksi internet.
- Pastikan token valid.
- Pastikan akun pengguna memenuhi pembatasan akses yang diterapkan bot.

## Keamanan

- **Jangan unggah `.env` ke GitHub.**
- Jangan pernah membagikan `BOT_TOKEN` di screenshot, chat, atau laporan bug.
- Jika token terlanjur bocor, cabut/ganti melalui BotFather lalu perbarui `.env`.
- Batasi `OWNER_ID` kepada akun yang dipercaya.
- Periksa isi folder sebelum menjalankan backup; semua file yang ditemukan dalam folder target akan dicoba untuk dikirim ke grup.

## Lisensi

Tambahkan lisensi ke repositori jika ingin orang lain menggunakan, mengubah, atau mendistribusikan proyek ini. Jika belum menentukan lisensi, jangan menyatakan proyek ini berlisensi tertentu.

---

**Catatan pengembangan:** README ini menjelaskan alur penggunaan untuk versi bot yang memiliki menu mode `1` dan `2`, perintah `--send`, serta `--send-folder`. Nama perintah atau fitur dapat berbeda jika `bot.py` di repositori berubah; perbarui dokumentasi setelah mengubah kode.
